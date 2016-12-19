#!/usr/bin/env python

# Run doctests in README.rst

# Imports {{{1
from __future__ import print_function
from runtests import (
    cmdLineOpts, writeSummary, succeed, fail,
    pythonCmd, coverageCmd,
)
import doctest
import sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent, coverage = cmdLineOpts()

# Unload the inform module so that it is reloaded during the doctests
# This is important because doctest replaces stdout with its own stream so it 
# can capture the output of the program being tested. Inform was imported from 
# runtests, and it already saved away stdout. By unloading it here, it will be 
# imported again after doctest has replaced stdout.
to_delete = [m for m in sys.modules.keys() if m.startswith('inform')]
for module in to_delete:
    del sys.modules[module]

# Tests {{{1
failures = tests_run = 0
for test in ['README.rst', 'inform/inform.py']:
    fails, tests = doctest.testfile(test, optionflags=doctest.ELLIPSIS)
    failures += fails
    tests_run += tests

if printSummary:
    result = fail('FAIL:') if failures else succeed('PASS:')
    print(result, tests_run, 'tests run,', failures, 'failures detected.')

writeSummary(tests_run, failures)
exit(failures != 0)
