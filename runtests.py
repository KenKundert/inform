# Utility for Recursively Running Self Tests
# TODO {{{1
# Support for coverage is weak because the coverage tool needs to be run
#     hierarchically from the current working directory whereas this tool walks 
#     the hierarchy running tests. Probably need a different tool for coverage.
# Consider adding support for functional and unit tests
# Consider adding the number of suites expected in the test script and complain
#     if the number of suites run is not right. This might be annoying to
#     maintain as if you add a test suite at the deepest level, all test files
#     above it would need to be modified.
# Provide a quiet option. Make it default when running hierarchically.
# Provide the equivalent to the av summarize command, so that once a quiet run
#     is complete, the summarize command can generate the output as if quiet
#     were not specified, and both the test and the result is available in the
#     summary file so that I can run summary with either -r or -t.
# This could be a warm up to implementing hierarchical testing in AV.
# Provide a facility for test programs to add command line options and then 
#     access their values.

# Description {{{1
"""
Run Tests

Run tests in the current working directory and subdirectories
Expected to be called from a very minimal python test file such as:
    #!/usr/bin/env python
    import runtests

    tests = ['test1', 'test2', ...]
    runtests.runTests(tests)

The tests will be run and a summary produced. The tests can either be files,
which are expected to be python files (without the .py suffix) or directories,
which are expected to contain another such file named 'test'.

Each test is expected to produce a summary file that will be read to determine
the number of tests and failures that occurred during that test. The summary
file for a python script should be named './.test.name.sum'. The summary file
for a directory should be named './dir/.test.sum'. The invocation of runTests
will create a file in the current working directory named './.test.sum'. These
summary files should contain a dictionary with keys: 'tests', 'failures'.
"""

# preliminaries {{{1
# imports {{{2
from __future__ import division, print_function
import os, sys
from json import load as loadSummary, dump as dumpSummary
from inform import Color
import argparse

# Globals {{{2
status = Color('blue', 'dark')
info = Color('magenta', 'dark')
succeed = Color('green', 'dark')
fail = Color('red', 'dark')
warning = Color('yellow', 'dark')
error = Color('red', 'dark')
exception = Color('red', 'light')


# default python
def pythonCmd(version=None):
    version = version if version else "{0}.{1}".format(*sys.version_info)
    return "python{}".format(version)

def coverageCmd(version=None, source=None):
    version = version if version else "{0}.{1}".format(*sys.version_info)
    version = '-' + version if '.' in version else version
    cmd = ["coverage{}".format(version), 'run', '--append', '--branch']
    if source:
        cmd += ['--include', source]
    return ' '.join(cmd)

# command line processor {{{2
class CommandLine():
    def __init__(self):
        self.progName = os.path.split(sys.argv[0])[1]
        cmdline_parser = argparse.ArgumentParser(
            add_help=False, description="Utility for recursively running tests.")
        cmdline_parser.add_argument(
            'tests', nargs='*', default=None, help="test name", metavar='<test>')
        cmdline_parser.add_argument(
            '-f', '--fast', action='store_true',
            help="take any shortcuts possible to speed testing")
        cmdline_parser.add_argument(
            '-s', '--nosummary', action='store_false',
            help="do not print the summary of test results")
        cmdline_parser.add_argument(
            '-t', '--test-values', action='store_true', help="print the test values")
        cmdline_parser.add_argument(
            '-r', '--results', action='store_true', help="print the test results")
        cmdline_parser.add_argument(
            '-c', '--nocolor', action='store_false',
            help="do not use color to highlight test results")
        cmdline_parser.add_argument(
            '--coverage', nargs='?', default=False, help="run coverage analysis")
        cmdline_parser.add_argument(
            '-h', '--help', action='store_true', help="print usage information and exit")
        cmdline_parser.add_argument('--parent', nargs='?', default=False, help='do not use')
        self.cmdline_parser = cmdline_parser
        self.cmdline_args = None

    def add_arg(self, *args, **kwargs):
        self.cmdline_parser.add_argument(*args, **kwargs)

    def get_arg(self, name):
        return getattr(self.cmdline_args, name)

    def process(self):
        if self.cmdline_args:
            # command line has already been processed
            return

        # process the command line
        cmdline_args = self.cmdline_parser.parse_args()
        if cmdline_args.help:
            self.cmdline_parser.print_help()
            sys.exit()
        self.cmdline_args = cmdline_args

        # copy known options into attributes
        self.fast = cmdline_args.fast
        self.printResults = cmdline_args.results
        self.printTests = cmdline_args.test_values or self.printResults
        self.printSummary = cmdline_args.nosummary or self.printTests
        self.colorize = cmdline_args.nocolor
        self.coverage = cmdline_args.coverage
        self.parent = cmdline_args.parent
        self.args = cmdline_args.tests

        if not self.colorize:
            status.active = False
            info.active = False
            succeed.active = False
            fail.active = False
            warning.active = False
            error.active = False
            exception.active = False


# Install the command line processor
clp = CommandLine()

# cmdLineOpts {{{1
def cmdLineOpts():
    """
    get command line options using something like:
        fast, printSummary, printTests, printResults, colorize, parent = runtests.cmdLineOpts()
    """
    clp.process()

    return (
        clp.fast,
        clp.printSummary,
        clp.printTests,
        clp.printResults,
        clp.colorize,
        clp.parent,
        clp.coverage,
    )

# writeSummary {{{1
def writeSummary(tests, testFailures, suites = 1, suiteFailures = None):
    """
    write summary file
    """
    # name becomes program names as invoked with .py stripped off
    name = clp.progName if clp.progName[-3:] != '.py' else clp.progName[0:-3]
    if suiteFailures == None and suites == 1:
        suiteFailures = 1 if testFailures else 0
    assert tests >= testFailures
    assert suites >= suiteFailures
    try:
        with open('.%s.sum' % name, 'w') as f:
            dumpSummary({
                'tests': tests,
                'testFailures': testFailures,
                'suites': suites,
                'suiteFailures': suiteFailures
            }, f)
    except OSError as err:
        sys.exit(
            exception(
                "%s: summary file '%s': %s." % (
                    clp.progName, err.filename, err.strerror
                )
            )
        )

# runTests {{{1
def runTests(tests, pythonVers=None, source=None, pythonPath=None, testKey='test'):
    """
    run tests

    tests is a list of strings that contains the names of the tests to be
        run. If the test is a local python file, then it should be named
        <testKey>.<test>.py. If it is a directory, it should be named <test>.
    pythonCmd is the full python command to be used to run the test files. This
        can be used to specify optimization flags to python or the desired
        python version.
    pythonPath is the python path to be set when running the test files.
    testKey is used for two things. First, it is appended to the name of each
        test file. The idea is that each test file would be paired up with the
        file it tests. If the file being tested is spam.py then the test file
        would be <testKey>.spam.py. By separating the test code from the code
        it tests, we make the initial reading of the code faster when it is not
        being tested. Second, when testing the directory, the test script is
        expected to be named ./<test>/<testKey> (notice that there is no .py
        extension even though this would also be a python file).
    """
    clp.process()
    python = pythonCmd(pythonVers)

    if clp.printTests:
        print("Using %s." % python)

    if clp.coverage is not False:
        if os.path.exists('.coverage') and not clp.parent:
            os.remove('.coverage')
        if not source:
            source = clp.coverage if clp.coverage else ''
        clp.coverage = source
        python = coverageCmd(pythonVers, source)
    pythonPath = ('PYTHONPATH=%s; ' % pythonPath) if pythonPath else ''

    if len(clp.args) == 0:
        clp.args = tests

    failures = False
    numTests = 0
    numTestFailures = 0
    numSuites = 0
    numSuiteFailures = 0
    for test in clp.args:
        name = '%s/%s' % (clp.parent, test) if clp.parent else test
        if os.path.isfile('%s.%s.py' % (testKey, test)):
            summaryFileName = './.%s.%s.sum' % (testKey, test)
            deleteSummaryFile(summaryFileName)
            if clp.printSummary:
                sys.stdout.write(status('%s: ' % name))
                sys.stdout.flush()
            cmd = pythonPath + '%s %s.%s.py %s' % (
                python, testKey, test, _childOpts(test)
            )
            error = _invoke(cmd)
        elif os.path.isdir(test):
            summaryFileName = './%s/.%s.sum' % (test, testKey)
            deleteSummaryFile(summaryFileName)
            cmd = 'cd %s; %s %s %s' % (test, python, testKey, _childOpts(test))
            error = _invoke(cmd)
        else:
            print(exception(
                '%s: cannot find test %s, skipping.' % (
                    clp.progName, name
                )
            ))
            numSuites += 1
            numSuiteFailures += 1
            continue
        if error and not clp.coverage is not False:
            # return status of coverage seems broken (sigh)
            print(fail('Failures detected in %s tests.' % name))
            failures = True
        try:
            with open(summaryFileName) as f:
                results = loadSummary(f)
                numTests += results['tests']
                numTestFailures += results['testFailures']
                numSuites += results['suites']
                numSuiteFailures += results['suiteFailures']
        except KeyError:
            sys.exit(
                    exception(
                    '%s: invalid summary file: %s' % (
                        clp.progName, summaryFileName
                    )
                )
            )
        except OSError as err:
            if error:
                numSuites += 1
                numSuiteFailures += 1
            else:
                sys.exit(
                    exception(
                        "%s: summary file '%s': %s." % (
                            clp.progName, summaryFileName, err.strerror
                        )
                    )
                )

    if clp.printSummary and not clp.parent and len(clp.args) > 1:
        preamble = info('Composite results')
        synopsis = '%s of %s test suites failed, %s of %s tests failed.' % (
            numSuiteFailures, numSuites, numTestFailures, numTests
        )
        if numSuiteFailures or numTestFailures:
            print("%s: %s" % (preamble, fail("FAIL: %s" % synopsis)))
        else:
            print("%s: %s" % (preamble, succeed("PASS: %s" % synopsis)))

    try:
        writeSummary(numTests, numTestFailures, numSuites, numSuiteFailures)
    except OSError as err:
        sys.exit(
            exception(
                "%s: summary file '%s': %s." % (
                    clp.progName, summaryFileName, err.strerror
                )
            )
        )

    sys.exit(bool(failures))

# utilities {{{1
# _childOpts {{{2
# create command line options for the children
def _childOpts(test):
    opts = sys.argv[1:]
    opts = []
    if clp.fast: opts += ['-f']
    if not clp.printSummary: opts += ['-s']
    if clp.printTests: opts += ['-t']
    if clp.printResults: opts += ['-r']
    if not clp.colorize: opts += ['-c']
    if clp.parent:
        newParent = '%s/%s' % (clp.parent, test)
    else:
        newParent = test
    opts += ['--parent', newParent]
    if clp.coverage is not False:
        opts += ['--coverage']
        if clp.coverage:
            opts += [clp.coverage]
    return ' '.join(opts)

# _invoke {{{2
# invoke a shell command
def _invoke(cmd):
    try:
        return os.system(cmd)
    except OSError as err:
        sys.exit(
            exception(
                '\n'.join([
                    "%s: when running '%s':" % (sys.argv[0], cmd),
                    "%s: " % ((err.filename)) if err.filename else ''
                      + "%s." % (err.strerror)
                ])
            )
        )

# deleteSummaryFile {{{2
# delete a summary file (need to do this to assure we don't pick up a
# stale one if the test program fails to generate a new one). 
def deleteSummaryFile(filename):
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except OSError as err:
            sys.exit(
                exception(
                    "%s: summary file '%s': %s." % (
                        sys.argv[0], filename, err.strerror
                    )
                )
            )
