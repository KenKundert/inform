# encoding: utf8
# This file has a z in its name so that it is run last.  There is some
# dependency that I have not been able to track down that causes the other tests
# to fail if it goes first.

import pytest
import doctest
import glob
import sys


def test_README():
    if sys.version_info < (3, 6):
        # code used in doctests assumes python3.6
        return
    rv = doctest.testfile('../README.rst', optionflags=doctest.ELLIPSIS)
    assert rv.attempted == 29
    assert rv.failed == 0

def test_inform():
    if sys.version_info < (3, 6):
        # code used in doctests assumes python3.6
        return

    rv = doctest.testfile('../inform/inform.py', optionflags=doctest.ELLIPSIS)
    assert rv.attempted in [180, 181]
        # for some reasons 181 test are run on my laptop, and 180 on github
    assert rv.failed == 0

def test_manual():
    if sys.version_info < (3, 6):
        # code used in doctests assumes python3.6
        return
    expected_test_count = {
        '../doc/api.rst': 0,
        '../doc/examples.rst': 0,
        '../doc/index.rst': 35,
        '../doc/releases.rst': 0,
        '../doc/user.rst': 281,
    }
    found = glob.glob('../doc/*.rst')
    for f in found:
        assert f in expected_test_count, f
    for path, tests in expected_test_count.items():
        rv = doctest.testfile(path, optionflags=doctest.ELLIPSIS)
        assert rv.failed == 0, path
        assert rv.attempted == tests, path

if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.

    defined = dict(globals())
    for k, v in defined.items():
        if callable(v) and k.startswith('test_'):
            print()
            print('Calling:', k)
            print((len(k)+9)*'=')
            v()
