#!/usr/bin/env python3

# Run doctests in README.rst

# Imports {{{1
from runtests import cmdLineOpts, writeSummary
from textcolors import Colors
import doctest
import sys

# Initialization {{{1
fast, printSummary, printTests, printResults, colorize, parent = cmdLineOpts()

colors = Colors(colorize)
succeed = colors.colorizer('green')
fail = colors.colorizer('red')
error = colors.colorizer('red')
info = colors.colorizer('magenta')
status = colors.colorizer('cyan')

failures, testsRun = doctest.testfile("README.rst", optionflags=doctest.ELLIPSIS)
if printSummary:
    state = fail('FAIL:') if failures else succeed('PASS:')
    print(state, '%s tests run, %s failures detected.' % (testsRun, failures))

writeSummary(testsRun, failures)
exit(failures != 0)
