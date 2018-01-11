# encoding: utf8

from inform import (
    Color, columns, conjoin, cull, fmt, full_stop, indent,
    is_collection, is_iterable, is_str, join, os_error, plural, render,
    ddd, ppp, sss, vvv
)
from textwrap import dedent
import sys
import pytest

# Before Python3.5 the dictionaries were ordered randomly, which confuses the
# test. This is a crude fix, just sort the output, that way we will likely catch
# most unexpected changes.  This is not needed for 3.6 and beyond.
if sys.version_info < (3, 6):
    def X(arg):
        return sorted(arg)
else:
    def X(arg):
        return arg

def test_debug(capsys):
    a='a'
    b='b'
    c='c'
    ddd(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py:26, test_utilities.test_debug():
            'a'
            'b'
            'c'
    """).lstrip()

    ddd(a=a, b=b, c=c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py:35, test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    ppp(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py:44, test_utilities.test_debug():
            a b c
    """).lstrip()

    vvv(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py:51, test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    sss()
    captured = capsys.readouterr()
    assert captured[0].split('\n')[0] == "DEBUG: test_utilities.py:60, test_utilities.test_debug():"

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
    assert cull([None, 0, 1, 2]) == [1, 2]
    assert cull([None, 0, 1, 2], remove=None) == [0, 1, 2]
    assert cull([None, 0, 1, 2], remove=0) == [None, 1, 2]
    assert cull([None, 0, 1, 2], remove=(1, 2)) == [None, 0]
    assert cull({1:0, 2:1, 0:2}, ) == {2:1, 0:2}

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
    n={
        'c': 'y',
        'e': 'x',
        'a': 'z',
    }
    assert render(n, sort=True) == "{'a': 'z', 'c': 'y', 'e': 'x'}"
    n={
        'c': 'y',
        'e': 'x',
        None: 'z',
    }
    if sys.version_info >= (3, 6):
        assert render(n, sort=True) == "{'c': 'y', 'e': 'x', None: 'z'}"

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

def test_color():
    assert Color('black')('black') == '\x1b[0;30mblack\x1b[0m'
    assert Color('red')('red') == '\x1b[0;31mred\x1b[0m'
    assert Color('green')('green') == '\x1b[0;32mgreen\x1b[0m'
    assert Color('yellow')('yellow') == '\x1b[0;33myellow\x1b[0m'
    assert Color('blue')('blue') == '\x1b[0;34mblue\x1b[0m'
    assert Color('magenta')('magenta') == '\x1b[0;35mmagenta\x1b[0m'
    assert Color('cyan')('cyan') == '\x1b[0;36mcyan\x1b[0m'
    assert Color('white')('white') == '\x1b[0;37mwhite\x1b[0m'
    assert Color.strip_colors(Color('red')('red')) == 'red'

def test_join():
    assert join('a', 'b', 'c') == 'a b c'
    assert join('a', 'b', 'c', sep='-') == 'a-b-c'
    assert join('a', 'b', 'c', x='x', y='y', template='{}, x={x}') == 'a, x=x'
    assert join('Lorem\nipsum\ndolor', wrap=100) == 'Lorem ipsum dolor'
    c=dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
        minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    ''').strip()
    d=dedent('''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
        et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
        cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    ''').strip()
    assert join(c, wrap=100) == d
    assert join(d, wrap=True) == c
    disappointments = [
        dict(key='abby', name='Abby Normal', desc='team captain'),
        dict(key='dizzy', name='Dizzy Functional'),
        dict(key='trump'),
    ]
    assert join(
        key='abby', name='Abby Normal', desc='team captain',
        template=('{key}: {name} -- {desc}', '{key}: {name}')
    ) == 'abby: Abby Normal -- team captain'

    assert join(
        key='dizzy', name='Dizzy Functional',
        template=('{key}: {name} -- {desc}', '{key}: {name}')
    ) == 'dizzy: Dizzy Functional'

    with pytest.raises(KeyError) as exception:
        assert join(
            key='trump',
            template=('{key}: {name} -- {desc}', '{key}: {name}')
        )
    assert str(exception.value) == "'no template match.'"

def test_columns():
    phonetic = sorted('''
        Alfa Echo India Mike Quebec Uniform Yankee Bravo Foxtrot Juliett
        November Romeo Victor Zulu Charlie Golf Kilo Oscar Sierra Whiskey Delta
        Hotel Lima Papa Tango X-ray
    '''.split())
    expected = indent(dedent('''
        Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
        Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
        Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
        Delta     Hotel     Lima      Papa      Tango     X-ray
    ''').strip())
    assert columns(phonetic) == expected

