#!/usr/bin/env python3

# Test Inform and the Informant Generator

# Imports {{{1
from __future__ import print_function
from runtests import (
    cmdLineOpts, writeSummary, succeed, fail, info, status, warning,
    pythonCmd, coverageCmd,
)
from inform import indent
from textwrap import dedent
from difflib import Differ
from importlib import import_module
import re
import sys
if sys.version[0] == '2':
    # io assumes unicode, which python2 does not provide by default
    # so use StringIO instead
    from StringIO import StringIO
    # Add support for with statement by monkeypatching
    StringIO.__enter__ = lambda self: self
    StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
else:
    from io import StringIO
import os
assert __debug__


# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent, coverage = cmdLineOpts()

if coverage is False:
    python = pythonCmd()
else:
    python = coverageCmd(source=coverage)

# Utilities {{{1
def format(text):
    try:
        if '\n' in text:
            return '\n' + indent(text, '        ')
        else:
            return text
    except:
        return text

invokeExecutableRegex = r"\w+: invoked as: \w+(?=\n)"
invokeTimeRegex = r"\w+: log opened on [^\n]+(?=\n)"
def stripInvokeInfo(text):
    text = re.sub(invokeExecutableRegex, 'inform: invoked as: <exe>', text)
    text = re.sub(invokeTimeRegex, 'inform: log opened on <date>', text)
    return text

# showDiff {{{2
def showDiff(achieved, expected, indent=''):
    diff = Differ().compare(
        expected.splitlines(),
        achieved.splitlines()
    )
    for each in diff:
        if each[0] == '+':
            print(indent+succeed(each))
        elif each[0] == '-':
            print(indent+info(each))
        elif each[0] == '?':
            print(indent+status(each))
        else:
            print(indent+each)


# Case class {{{1
class Case():
    names = set()
    inform = import_module('inform')

    def __init__(self, name, stimulus, stdout='', stderr='', logfile=''):
        self.name = name
        self.stimulus = stimulus.strip()
        assert name not in Case.names
        Case.names.add(name)
        self.expected_output = stdout.strip()
        self.expected_error = stderr.strip()
        self.expected_log = logfile.strip()

    def __str__(self):
        return '%s<%s>' % (self.__class__.__name__, self.name)

    __repr__ = __str__

    def run(self):
        sys.argv = [case.name]
        try:
            with StringIO() as stdout, \
                 StringIO() as stderr, \
                 StringIO() as logfile:
                test_locals = {
                    'stdout': stdout,
                    'stderr': stderr,
                    'logfile': logfile,
                }
                test_globals = Case.inform.__dict__
                exec(self.stimulus, test_globals, test_locals)
                self.output = stdout.getvalue().strip()
                self.error = stderr.getvalue().strip()
                self.log = stripInvokeInfo(logfile.getvalue().strip())

        except Exception as err:
            return (self.name, self.stimulus, str(err), None, 'exception')

        if self.error != self.expected_error:
            return (self.name, self.stimulus, self.error, self.expected_error, 'stderr result')
        if self.output != self.expected_output:
            return (self.name, self.stimulus, self.output, self.expected_output, 'stdout result')
        if self.log != self.expected_log:
            return (self.name, self.stimulus, self.log, self.expected_log, 'logfile result')


# Stop class {{{1
class Exit(Case):
    def __init__(self):
        pass

    def run(self):
        sys.exit('TERMINATING TESTS UPON DEVELOPER REQUEST')

# Test cases {{{1
captureAll = ', '.join([
    'logfile=logfile',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name="inform"',
])
noLog = ', '.join([
    'logfile=False',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name="inform"',
])
noProg = ', '.join([
    'logfile=logfile',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name=False',
])
yesProg = ', '.join([
    'logfile=logfile',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name=True',
])
noHang = ', '.join([
    'logfile=logfile',
    'stdout=stdout',
    'stderr=stderr',
    'prog_name="inform"',
    'hanging_indent=False',
])
fmtStim = dedent("""\
    Inform({stdargs})
    def func1():
        def func2():
            def func3():
                lvl = 3
                try:
                    display(fmt('func3 -> {{lvl}}', _lvl={lvl}))
                except KeyError as err:
                    display("'lvl' not found in func3")
            lvl = 2
            try:
                display(fmt('func2 -> {{lvl}}', _lvl={lvl}))
            except KeyError as err:
                display("'lvl' not found in func2")
            func3()
        lvl = 1
        try:
            display(fmt('func1 -> {{lvl}}', _lvl={lvl}))
        except KeyError as err:
            display("'lvl' not found in func1")
        func2()
    lvl = 0
    try:
        display(fmt('func0 -> {{lvl}}', _lvl={lvl}))
    except KeyError as err:
        display("'lvl' not found in func0")
    func1()
""")
testCases = [
    Case(
        name='endeavor',
        stimulus=dedent('''
            Inform({stdargs})
            output('this is a test.')
        '''.format(stdargs=noLog)),
        stdout="this is a test.",
    ),
    Case(
        name='kestrel',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='overspend',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='alarm',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test', sep='_', end='.{nl}')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout="This_is_a_test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This_is_a_test.
        '''),
    ),
    Case(
        name='canalize',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is an ...{nl}    output test!')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout="This is an ...\n    output test!",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is an ...
                output test!
        '''),
    ),
    Case(
        name='marshy',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is an ...{nl}    output test!', hanging=False)
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout="This is an ...\n    output test!",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is an ...
                output test!
        '''),
    ),
    Case(
        name='harden',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='outflank',
        stimulus=dedent('''
            Inform(verbose=True, {stdargs})
            comment('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='elope',
        stimulus=dedent('''
            Inform({stdargs})
            comment('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='sunset',
        stimulus=dedent('''
            Inform(narrate=True, {stdargs})
            narrate('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='wheezy',
        stimulus=dedent('''
            Inform({stdargs})
            narrate('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='claim',
        stimulus=dedent('''
            Inform({stdargs})
            display('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='behind',
        stimulus=dedent('''
            Inform(quiet=True, {stdargs})
            display('This is a test.')
        '''.format(stdargs=captureAll)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='overhead',
        stimulus=dedent('''
            Inform({stdargs})
            debug('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform DEBUG: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform DEBUG: This is a test.
        '''),
    ),
    Case(
        name='instill',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform warning: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning: This is a test.
        '''),
    ),
    Case(
        name='workhouse',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a ...{nl}test.')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout=dedent('''
            inform warning:
                This is a ...
                test.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning:
                This is a ...
                test.
        '''),
    ),
    Case(
        name='flounder',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a ...{nl}test.', hanging=False)
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout=dedent('''
            inform warning:
                This is a ...
                test.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning:
                This is a ...
                test.
        '''),
    ),
    Case(
        name='blister',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=captureAll)),
        stdout="inform error: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a test.
        '''),
    ),
    Case(
        name='blacken',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=noProg)),
        stdout="error: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            error: This is a test.
        '''),
    ),
    Case(
        name='lattice',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
            codicil('This is an appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform warning: This is a test.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning: This is a test.
                This is an appendage.
        '''),
    ),
    Case(
        name='seventh',
        stimulus=dedent('''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
    ),
    Case(
        name='primary',
        stimulus=dedent(r'''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage,\nand the third.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error
                This is the first appendage.
                This is the second appendage,
                and the third.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error
                This is the first appendage.
                This is the second appendage,
                and the third.
        '''),
    ),
    Case(
        name='sensitize',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is main message.')
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
    ),
    Case(
        name='mullah',
        stimulus=dedent(r'''
            Inform({stdargs})
            error('Error message.\nAdditional info.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error:
                Error message.
                Additional info.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error:
                Error message.
                Additional info.
        '''),
    ),
    Case(
        name='thwart',
        stimulus=dedent('''
            Inform({stdargs})
            output('this is a test.', culprit='src')
        '''.format(stdargs=captureAll)),
        stdout="src: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            src: this is a test.
        '''),
    ),
    Case(
        name='bivouac',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is a test.', culprit='src')
        '''.format(stdargs=captureAll)),
        stdout="inform error: src: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src: this is a test.
        '''),
    ),
    Case(
        name='remote',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is the ...{nl}error message.', culprit='src')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout=dedent('''
            inform error: src:
                this is the ...
                error message.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src:
                this is the ...
                error message.
        '''),
    ),
    Case(
        name='pillbox',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is a test.', culprit='src1 src2 src3'.split())
        '''.format(stdargs=captureAll)),
        stdout="inform error: src1, src2, src3: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src1, src2, src3: this is a test.
        '''),
    ),
    Case(
        name='suppurate',
        stimulus=dedent('''
            Inform({stdargs})
            output(
                'This is the body of the output message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the output message.
            This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the output message.
            This is an appendage.
        '''),
    ),
    Case(
        name='patrol',
        stimulus=dedent('''
            Inform({stdargs})
            error(
                'This is the body of the error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        '''.format(stdargs=captureAll)),
        stdout=dedent('''
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the error message.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the error message.
                This is an appendage.
        '''),
    ),
    Case(
        name='chattel',
        stimulus=dedent('''
            Inform({stdargs})
            error(
                'This is the body of the ...{nl}error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout=dedent('''
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
                This is an appendage.
        '''),
    ),
    Case(
        name='unknown',
        stimulus=dedent('''
            Inform({stdargs})
            output(
                'This is the body of the ...{nl}error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        ''').format(stdargs=captureAll, nl=r'\n'),
        stdout=dedent('''
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
            This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
            This is an appendage.
        '''),
    ),
    Case(
        name='elongate',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=noHang)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='totter',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test.')
        '''.format(stdargs=noHang)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='chieftain',
        stimulus=dedent('''
            Inform({stdargs})
            output('This', 'is', 'a', 'test', sep='_', end='.{nl}')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout="This_is_a_test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This_is_a_test.
        '''),
    ),
    Case(
        name='junction',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is an ...{nl}    output test!')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout="This is an ...\n    output test!",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is an ...
                output test!
        '''),
    ),
    Case(
        name='energy',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is an ...{nl}    output test!', hanging=True)
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout="This is an ...\n    output test!",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is an ...
                output test!
        '''),
    ),
    Case(
        name='accordion',
        stimulus=dedent('''
            Inform({stdargs})
            log('This is a test.')
        '''.format(stdargs=noHang)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='church',
        stimulus=dedent('''
            Inform(verbose=True, {stdargs})
            comment('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='symbol',
        stimulus=dedent('''
            Inform({stdargs})
            comment('This is a test.')
        '''.format(stdargs=noHang)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='emperor',
        stimulus=dedent('''
            Inform(narrate=True, {stdargs})
            narrate('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='flirt',
        stimulus=dedent('''
            Inform({stdargs})
            narrate('This is a test.')
        '''.format(stdargs=noHang)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='stroller',
        stimulus=dedent('''
            Inform({stdargs})
            display('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='array',
        stimulus=dedent('''
            Inform(quiet=True, {stdargs})
            display('This is a test.')
        '''.format(stdargs=noHang)),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a test.
        '''),
    ),
    Case(
        name='butcher',
        stimulus=dedent('''
            Inform({stdargs})
            debug('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="inform DEBUG: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform DEBUG: This is a test.
        '''),
    ),
    Case(
        name='clumsy',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="inform warning: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning: This is a test.
        '''),
    ),
    Case(
        name='prayer',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a ...{nl}test.')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout=dedent('''
            inform warning:
                This is a ...
                test.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning:
                This is a ...
                test.
        '''),
    ),
    Case(
        name='visualize',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a ...{nl}test.', hanging=True)
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout=dedent('''
            inform warning:
                This is a ...
                test.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning:
                This is a ...
                test.
        '''),
    ),
    Case(
        name='discount',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=noHang)),
        stdout="inform error: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a test.
        '''),
    ),
    Case(
        name='scamper',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=noProg)),
        stdout="error: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            error: This is a test.
        '''),
    ),
    Case(
        name='olver',
        stimulus=dedent('''
            Inform({stdargs})
            error('This is a test.')
        '''.format(stdargs=yesProg)),
        stdout="olver error: This is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            olver error: This is a test.
        '''),
    ),
    Case(
        name='recline',
        stimulus=dedent('''
            Inform({stdargs})
            warn('This is a test.')
            codicil('This is an appendage.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            inform warning: This is a test.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform warning: This is a test.
                This is an appendage.
        '''),
    ),
    Case(
        name='litany',
        stimulus=dedent('''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            inform error
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error
                This is the first appendage.
                This is the second appendage.
                This is the third appendage.
        '''),
    ),
    Case(
        name='misspend',
        stimulus=dedent(r'''
            Inform({stdargs})
            error()
            codicil('This is the first appendage.')
            codicil('This is the second appendage,\nand the third.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            inform error
                This is the first appendage.
                This is the second appendage,
                and the third.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error
                This is the first appendage.
                This is the second appendage,
                and the third.
        '''),
    ),
    Case(
        name='protector',
        stimulus=dedent('''
            Inform({stdargs})
            output('This is main message.')
            codicil('This is the first appendage.')
            codicil('This is the second appendage.')
            codicil('This is the third appendage.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is main message.
            This is the first appendage.
            This is the second appendage.
            This is the third appendage.
        '''),
    ),
    Case(
        name='outhouse',
        stimulus=dedent(r'''
            Inform({stdargs})
            error('Error message.\nAdditional info.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            inform error:
                Error message.
                Additional info.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error:
                Error message.
                Additional info.
        '''),
    ),
    Case(
        name='fringe',
        stimulus=dedent('''
            Inform({stdargs})
            output('this is a test.', culprit='src')
        '''.format(stdargs=noHang)),
        stdout="src: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            src: this is a test.
        '''),
    ),
    Case(
        name='prosy',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is a test.', culprit='src')
        '''.format(stdargs=noHang)),
        stdout="inform error: src: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src: this is a test.
        '''),
    ),
    Case(
        name='vagrant',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is the ...{nl}error message.', culprit='src')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout=dedent('''
            inform error: src:
                this is the ...
                error message.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src:
                this is the ...
                error message.
        '''),
    ),
    Case(
        name='pirouette',
        stimulus=dedent('''
            Inform({stdargs})
            error('this is a test.', culprit='src1 src2 src3'.split())
        '''.format(stdargs=noHang)),
        stdout="inform error: src1, src2, src3: this is a test.",
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: src1, src2, src3: this is a test.
        '''),
    ),
    Case(
        name='relapse',
        stimulus=dedent('''
            Inform({stdargs})
            output(
                'This is the body of the output message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the output message.
            This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the output message.
            This is an appendage.
        '''),
    ),
    Case(
        name='bulwark',
        stimulus=dedent('''
            Inform({stdargs})
            error(
                'This is the body of the error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        '''.format(stdargs=noHang)),
        stdout=dedent('''
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the error message.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the error message.
                This is an appendage.
        '''),
    ),
    Case(
        name='novelty',
        stimulus=dedent('''
            Inform({stdargs})
            error(
                'This is the body of the ...{nl}error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout=dedent('''
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
                This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            inform error: This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
                This is an appendage.
        '''),
    ),
    Case(
        name='lockout',
        stimulus=dedent('''
            Inform({stdargs})
            output(
                'This is the body of the ...{nl}error message.',
                culprit='This is a very long culprit, indeed it is very very very very very very very long'
            )
            codicil('This is an appendage.')
        ''').format(stdargs=noHang, nl=r'\n'),
        stdout=dedent('''
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
            This is an appendage.
        '''),
        logfile=dedent('''
            inform: invoked as: <exe>
            inform: log opened on <date>
            This is a very long culprit, indeed it is very very very very very very very long:
                This is the body of the ...
                error message.
            This is an appendage.
        '''),
    ),
    Case(
        name='goner',
        stimulus=fmtStim.format(lvl=0, stdargs=noLog),
        stdout=dedent('''
            func0 -> 0
            func1 -> 1
            func2 -> 2
            func3 -> 3
        '''),
    ),
    Case(
        name='shadow',
        stimulus=fmtStim.format(lvl=-1, stdargs=noLog),
        stdout=dedent('''
            'lvl' not found in func0
            func1 -> 0
            func2 -> 1
            func3 -> 2
        '''),
    ),
    Case(
        name='curdle',
        stimulus=fmtStim.format(lvl=-2, stdargs=noLog),
        stdout=dedent('''
            'lvl' not found in func0
            'lvl' not found in func1
            func2 -> 0
            func3 -> 1
        '''),
    ),
]


# Run tests {{{1
testsRun = 0
failures = 0
for case in testCases:
    testsRun += 1
    if printTests:
        print(status('Trying %d (%s):' % (testsRun, case.name)), case.stimulus)

    failure = case.run()

    if failure:
        failures += 1
        name, stimulus, result, expected, kind = failure
        print(fail('Unexpected %s (%s):' % (kind, failures)))
        print(info('    Case    :'), name)
        print(info('    Given   :'), format(stimulus))
        print(info('    Result  :'), format(result))
        print(info('    Expected:'), format(expected))
        if result and expected:
            print(info('    Diff:'))
            showDiff(result, expected, indent=8*' ')


# Print test summary {{{1
numTests = len(testCases)
assert testsRun == numTests, "Incorrect number of tests run (%s of %s)." % (testsRun, numTests)
if printSummary:
    print('%s: %s tests run, %s failures detected.' % (
        fail('FAIL') if failures else succeed('PASS'), testsRun, failures
    ))

writeSummary(testsRun, failures)
sys.exit(int(bool(failures)))
