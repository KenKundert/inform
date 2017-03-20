# encoding: utf8

from inform import (
    conjoin, cull, fmt, full_stop, indent, is_collection, is_iterable, is_str,
    os_error, plural, render
)
from textwrap import dedent
import sys

# Before Python3.5 the dictionaries were ordered randomly, which confuses the
# test. This is a crude fix, just sort the output, that way we will likely catch
# most unexpected changes.  This is not needed for 3.6 and beyond.
if sys.version_info < (3, 5):
    def X(arg):
        return sorted(arg)
else:
    def X(arg):
        return arg

def test_indent():
    text=dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
        non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    ''').strip()

    assert '<\n' + indent(text) + '\n>' == dedent('''\
    <
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
        non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    >''')

    assert '<\n' + indent(text, leader='  ') + '\n>' == dedent('''\
    <
      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
      tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
      quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
      consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
      cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
      non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    >''')

    assert '<\n' + indent(text, first=-1) + '\n>' == dedent('''\
    <
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
        non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    >''')

    assert '<\n' + indent(text, first=1, stops=0) + '\n>' == dedent('''\
    <
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    >''')

def test_conjoin():
    items = ['a', 'b', 'c']

    assert conjoin(items) == 'a, b and c'
    assert conjoin(items, conj=', or ') == 'a, b, or c'
    assert conjoin(items, conj=' or ', sep='; ') == 'a; b or c'

def test_cull():
    assert cull([0, 1, 2]) == [1, 2]
    assert cull([False, 1, 2]) == [1, 2]
    assert cull([None, 1, 2]) == [1, 2]
    assert cull([[], 1, 2]) == [1, 2]
    assert cull([(), 1, 2]) == [1, 2]
    assert cull([{}, 1, 2]) == [1, 2]
    assert cull([set(), 1, 2]) == [1, 2]
    assert cull([0, 1, 2], remove=None) == [0, 1, 2]
    assert cull([False, 1, 2], remove=None) == [False, 1, 2]
    assert cull([None, 1, 2], remove=None) == [1, 2]
    assert cull([None, 1, 2], remove=False) == [None, 1, 2]
    assert cull([False, 1, 2], remove=False) == [1, 2]
    assert cull([False, 1, 2], remove=lambda x: x==2) == [False, 1]

def test_fmt():
    a = 'a'
    b = 'b'
    c = 'c'
    assert fmt('{a}, {b}, {c}') == 'a, b, c'
    assert fmt('{0}, {1}, {2}', a, b, c) == 'a, b, c'
    assert fmt('{a}, {b}, {c}', a=a, b=b, c=c) == 'a, b, c'

    def func1():
        def func2():
            def func3():
                lvl = 3
                assert fmt('func3 -> {lvl}', _level=1) == 'func3 -> 3'
            lvl = 2
            assert fmt('func2 -> {lvl}', _level=1) == 'func2 -> 2'
            func3()
        lvl = 1
        assert fmt('func1 -> {lvl}', _level=1) == 'func1 -> 1'
        func2()
    lvl = 0
    assert fmt('func0 -> {lvl}', _level=1) == 'func0 -> 0'
    func1()

def test_render():
    x=5
    y=6
    a="this is a test"
    b="this is another test"
    c=dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
        non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    ''')
    d={'x':x, 'y':y}
    e=(1,2,3)
    f={1,2,3}
    F={1,None,3}
    g=[1,2,3]
    h={
        'a': a,
        'b': b,
        'c': c,
        'd': d,
        'e': e,
        'f': f,
        'g': g,
    }
    i={
        'a': a,
        'b': b,
        'c': c,
        'd': d,
        'e': e,
        'f': f,
        'g': g,
        'h': h,
    }

    assert render(x) == '5'
    assert render(y) == '6'
    assert render(a) == "'this is a test'"
    assert render(b) == "'this is another test'"
    assert render(c) == dedent('''\
    """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
        non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    """''')
    assert X(render(d)) == X("{'x': 5, 'y': 6}")
    assert render(e) == "(1, 2, 3)"
    assert render(f) == "{1, 2, 3}"
    assert sorted(render(F)) == sorted("{1, None, 3}")
    assert render(g) == "[1, 2, 3]"
    assert X(render(h)) == X(dedent('''\
    {
        'a': 'this is a test',
        'b': 'this is another test',
        'c': """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
            cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
            non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """,
        'd': {'x': 5, 'y': 6},
        'e': (1, 2, 3),
        'f': {1, 2, 3},
        'g': [1, 2, 3],
    }'''))
    assert X(render(i)) == X(dedent('''\
    {
        'a': 'this is a test',
        'b': 'this is another test',
        'c': """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
            cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
            non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """,
        'd': {'x': 5, 'y': 6},
        'e': (1, 2, 3),
        'f': {1, 2, 3},
        'g': [1, 2, 3],
        'h': {
            'a': 'this is a test',
            'b': 'this is another test',
            'c': """
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
                non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            """,
            'd': {'x': 5, 'y': 6},
            'e': (1, 2, 3),
            'f': {1, 2, 3},
            'g': [1, 2, 3],
        },
    }'''))

def test_plural():
    assert plural(0, 'baby', 'babies') == 'babies'
    assert plural(1, 'baby', 'babies') == 'baby'
    assert plural(2, 'baby', 'babies') == 'babies'
    assert plural(0, 'boy') == 'boys'
    assert plural(1, 'boy') == 'boy'
    assert plural(2, 'boy') == 'boys'
    assert plural([], 'boy') == 'boys'
    assert plural(['carl'], 'boy') == 'boy'
    assert plural(['carl', 'george'], 'boy') == 'boys'

def test_full_stop():
    assert full_stop('hey now') == 'hey now.'
    assert full_stop('hey now.') == 'hey now.'
    assert full_stop('hey now?') == 'hey now?'
    assert full_stop('hey now!') == 'hey now!'

def test_os_error():
    try:
        open('/')
        assert False
    except (OSError, IOError) as err:
        assert os_error(err) == '/: is a directory.'

def test_is_str():
    assert is_str(0) == False
    assert is_str('') == True

def test_is_iterable():
    assert is_iterable(0) == False
    assert is_iterable('') == True
    assert is_iterable([]) == True
    assert is_iterable(()) == True
    assert is_iterable({}) == True

def test_is_collection():
    assert is_collection(0) == False
    assert is_collection('') == False
    assert is_collection([]) == True
    assert is_collection(()) == True
    assert is_collection({}) == True
