#!/usr/bin/env python

# Run doctests in README.rst

# Imports {{{1
from __future__ import print_function
from runtests import (
    cmdLineOpts, writeSummary, succeed, fail, status,
    pythonCmd, coverageCmd,
)
import doctest
import sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent, coverage = cmdLineOpts()

# use the inform color package before unloading it.
failure = fail('FAIL:')
success = succeed('PASS:')
trying = status('Trying:')

# Unload the inform module so that it is reloaded during the doctests
# This is needed because doctest replaces stdout with its own stream so it 
# can capture the output of the program being tested. Inform was imported from 
# runtests, and it already saved away stdout. By unloading it here, it will be 
# imported again after doctest has replaced stdout.
def unload_inform():
    to_delete = [m for m in sys.modules.keys() if m.startswith('inform')]
    for module in to_delete:
        del sys.modules[module]

if coverage is False:
    python = pythonCmd()
else:
    python = coverageCmd(source=coverage)

tests = '''
    README.rst inform/inform.py doc/api.rst doc/examples.rst doc/index.rst
    doc/user.rst
'''.split()

# Tests {{{1
failures = tests_run = 0
for test in tests:
    if printTests:
        print(trying, test)
    unload_inform()
    fails, tests = doctest.testfile(test, optionflags=doctest.ELLIPSIS)
    failures += fails
    tests_run += tests

if printSummary:
    result = failure if failures else success
    print(result, tests_run, 'tests run,', failures, 'failures detected.')

writeSummary(tests_run, failures)
exit(failures != 0)
