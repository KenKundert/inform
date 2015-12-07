#!/usr/bin/env python3

# Run doctests in README.rst

# Imports {{{1
from runtests import cmdLineOpts, writeSummary, succeed, fail
import doctest
import sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()

# Unload the messenger module so that it is reloaded during the doctests
# This is important because doctest replaces stdout with its own stream so it 
# can capture the output of the program being tested. Messenger was imported 
# from runtests, and it already saved away stdout. By unloading it here, it 
# will be imported again after doctest has replaced stdout.
del sys.modules['messenger']

failures, testsRun = doctest.testfile("README.rst", optionflags=doctest.ELLIPSIS)
if printSummary:
    result = fail('FAIL:') if failures else succeed('PASS:')
    print(result, '%s tests run, %s failures detected.' % (testsRun, failures))

writeSummary(testsRun, failures)
exit(failures != 0)
