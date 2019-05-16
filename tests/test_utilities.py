# encoding: utf8

from inform import (
    Color, columns, conjoin, comment, cull, display, done, error, Error, fatal,
    fmt, full_stop, indent, Inform, is_collection, is_iterable, is_mapping,
    is_str, join, get_prog_name, get_informer, narrate, os_error, output,
    plural, render, terminate, warn, ddd, ppp, sss, vvv, ProgressBar,
)
from textwrap import dedent
import sys
import pytest

# Before Python3.5 the dictionaries were ordered randomly, which confuses the
# test. This is a crude fix, just sort the output, that way we will likely catch
# most unexpected changes.  This is not needed for 3.6 and beyond.
if sys.version_info < (3, 6):
    def X(arg):
        return '\n'.join(sorted(arg.split('\n')))
else:
    def X(arg):
        return arg

def test_debug(capsys):
    Inform(colorscheme=None, prog_name=False)
    a='a'
    b='b'
    c='c'
    ddd(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 28, test_utilities.test_debug():
            'a'
            'b'
            'c'
    """).lstrip()

    ddd(a=a, b=b, c=c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 37, test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    ppp(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 46, test_utilities.test_debug(): a b c
    """).lstrip()

    vvv(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 52, test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    sss()
    captured = capsys.readouterr()
    assert captured[0].split('\n')[0] == "DEBUG: test_utilities.py, 61, test_utilities.test_debug():"

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
    assert cull({1:0, 2:1, 0:2}) == {2:1, 0:2}
    assert set(cull({1:0, 2:1, 0:2}.keys(), remove=1)) == set([0, 2])
    assert set(cull({1:0, 2:1, 0:2}.values())) == set([1, 2])

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

    # These tests check the ability to use render in a class __repr__.
    class AAA:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __repr__(self):
            if self.kwargs.get('fault'):
                raise NotImplementedError
            return render(dict(args=self.args, kwargs=self.kwargs))

    aaa = AAA('aaa', thisis='aaa')
    bbb = AAA('bbb', thisis='bbb', child=aaa)
    ccc = AAA('ccc', thisis='ccc', child=bbb)
    ddd = AAA('ddd', thisis='ddd', fault=True)
    eee = AAA('eee', thisis='eee', child=ddd)
    fff = AAA('fff', thisis='fff', child=eee)

    bbb_expected_sorted = dedent('''
    {
        'args': ('bbb'),
        'kwargs': {
            'child': {
                'args': ('aaa'),
                'kwargs': {'thisis': 'aaa'},
            },
            'thisis': 'bbb',
        },
    }
    ''').strip()
    assert render(bbb, sort=True) == bbb_expected_sorted

    ccc_expected_unsorted = dedent('''
    {
        'args': ('ccc'),
        'kwargs': {
            'thisis': 'ccc',
            'child': {
                'args': ('bbb'),
                'kwargs': {
                    'thisis': 'bbb',
                    'child': {
                        'args': ('aaa'),
                        'kwargs': {'thisis': 'aaa'},
                    },
                },
            },
        },
    }
    ''').strip()
    if sys.version_info >= (3, 6):
        assert render(ccc) == ccc_expected_unsorted

    ccc_expected_sorted = dedent('''
    {
        'args': ('ccc'),
        'kwargs': {
            'child': {
                'args': ('bbb'),
                'kwargs': {
                    'child': {
                        'args': ('aaa'),
                        'kwargs': {'thisis': 'aaa'},
                    },
                    'thisis': 'bbb',
                },
            },
            'thisis': 'ccc',
        },
    }
    ''').strip()
    assert render(ccc, sort=True) == ccc_expected_sorted

    try:
        render(fff, sort=True)
    except NotImplementedError:
        pass

    if sys.version_info >= (3, 6):
        assert render(ccc) == ccc_expected_unsorted

    assert render(ccc, sort=True) == ccc_expected_sorted


    # test ability to render inform-aware classes
    class Chimera:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
        def _inform_get_args(self):
            return self.args
        def _inform_get_kwargs(self):
            return self.kwargs

    lycia = Chimera('Lycia', front='lion', middle='goat', tail='snake')
    assert render(lycia) == dedent('''
        Chimera(
            'Lycia',
            front='lion',
            middle='goat',
            tail='snake',
        )
    ''').strip()


def test_plural():
    assert '{:cart/s}'.format(plural(0)) == 'carts'
    assert '{:cart/s}'.format(plural(1)) == 'cart'
    assert '{:cart/s}'.format(plural(2)) == 'carts'
    assert '{:# cart/s}'.format(plural(0)) == '0 carts'
    assert '{:# cart/s}'.format(plural(1)) == '1 cart'
    assert '{:# cart/s}'.format(plural(2)) == '2 carts'
    assert '{:/baby/babies}'.format(plural(0)) == 'babies'
    assert '{:bab/y/ies}'.format(plural(0)) == 'babies'
    assert '{:/baby/babies}'.format(plural(1)) == 'baby'
    assert '{:bab/y/ies}'.format(plural(1)) == 'baby'
    assert '{:/baby/babies}'.format(plural(2)) == 'babies'
    assert '{:bab/y/ies}'.format(plural(2)) == 'babies'
    assert '{:# /baby/babies}'.format(plural(0)) == '0 babies'
    assert '{:# bab/y/ies}'.format(plural(0)) == '0 babies'
    assert '{:# /baby/babies}'.format(plural(1)) == '1 baby'
    assert '{:# bab/y/ies}'.format(plural(1)) == '1 baby'
    assert '{:# /baby/babies}'.format(plural(2)) == '2 babies'
    assert '{:# bab/y/ies}'.format(plural(2)) == '2 babies'
    assert '{:# boy/s}'.format(plural(''.split())) == '0 boys'
    assert '{:# boy/s}'.format(plural('carl'.split())) == '1 boy'
    assert '{:# boy/s}'.format(plural('carl george'.split())) == '2 boys'
    assert '{:# boy/s}'.format(plural(range(0))) == '0 boys'
    assert '{:# boy/s}'.format(plural(range(1))) == '1 boy'
    assert '{:# boy/s}'.format(plural(range(2))) == '2 boys'

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

def test_is_mapping():
    assert is_mapping(0) == False
    assert is_mapping('') == False
    assert is_mapping([]) == False
    assert is_mapping(()) == False
    assert is_mapping({}) == True

def test_color():
    assert Color('black', 'dark')('black') == '\x1b[0;30mblack\x1b[0m'
    assert Color('red', 'dark')('red') == '\x1b[0;31mred\x1b[0m'
    assert Color('green', 'dark')('green') == '\x1b[0;32mgreen\x1b[0m'
    assert Color('yellow', 'dark')('yellow') == '\x1b[0;33myellow\x1b[0m'
    assert Color('blue', 'dark')('blue') == '\x1b[0;34mblue\x1b[0m'
    assert Color('magenta', 'dark')('magenta') == '\x1b[0;35mmagenta\x1b[0m'
    assert Color('cyan', 'dark')('cyan') == '\x1b[0;36mcyan\x1b[0m'
    assert Color('white', 'dark')('white') == '\x1b[0;37mwhite\x1b[0m'

    assert Color('black', 'light')('black') == '\x1b[1;30mblack\x1b[0m'
    assert Color('red', 'light')('red') == '\x1b[1;31mred\x1b[0m'
    assert Color('green', 'light')('green') == '\x1b[1;32mgreen\x1b[0m'
    assert Color('yellow', 'light')('yellow') == '\x1b[1;33myellow\x1b[0m'
    assert Color('blue', 'light')('blue') == '\x1b[1;34mblue\x1b[0m'
    assert Color('magenta', 'light')('magenta') == '\x1b[1;35mmagenta\x1b[0m'
    assert Color('cyan', 'light')('cyan') == '\x1b[1;36mcyan\x1b[0m'
    assert Color('white', 'light')('white') == '\x1b[1;37mwhite\x1b[0m'

    assert Color('black')('black', scheme='dark') == '\x1b[0;30mblack\x1b[0m'
    assert Color('red')('red', scheme='dark') == '\x1b[0;31mred\x1b[0m'
    assert Color('green')('green', scheme='dark') == '\x1b[0;32mgreen\x1b[0m'
    assert Color('yellow')('yellow', scheme='dark') == '\x1b[0;33myellow\x1b[0m'
    assert Color('blue')('blue', scheme='dark') == '\x1b[0;34mblue\x1b[0m'
    assert Color('magenta')('magenta', scheme='dark') == '\x1b[0;35mmagenta\x1b[0m'
    assert Color('cyan')('cyan', scheme='dark') == '\x1b[0;36mcyan\x1b[0m'
    assert Color('white')('white', scheme='dark') == '\x1b[0;37mwhite\x1b[0m'

    assert Color('black')('black', scheme='light') == '\x1b[1;30mblack\x1b[0m'
    assert Color('red')('red', scheme='light') == '\x1b[1;31mred\x1b[0m'
    assert Color('green')('green', scheme='light') == '\x1b[1;32mgreen\x1b[0m'
    assert Color('yellow')('yellow', scheme='light') == '\x1b[1;33myellow\x1b[0m'
    assert Color('blue')('blue', scheme='light') == '\x1b[1;34mblue\x1b[0m'
    assert Color('magenta')('magenta', scheme='light') == '\x1b[1;35mmagenta\x1b[0m'
    assert Color('cyan')('cyan', scheme='light') == '\x1b[1;36mcyan\x1b[0m'
    assert Color('white')('white', scheme='light') == '\x1b[1;37mwhite\x1b[0m'

    assert Color('black', scheme=None)('black') == 'black'
    assert Color('black')('black', scheme=None) == 'black'

    Inform(colorscheme=None)
    assert Color('black')('black') == 'black'
    Inform(colorscheme='dark')
    assert Color('black')('black') == '\x1b[0;30mblack\x1b[0m'
    Inform(colorscheme='light')
    assert Color('black')('black') == '\x1b[1;30mblack\x1b[0m'
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

def test_stream_policy(capsys):
    with Inform(stream_policy='termination', prog_name=False):
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'warning: hey now!\n'
        assert captured[1] == ''
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hey now!\n'
        assert captured[1] == ''

    with Inform(stream_policy='header', prog_name=False):
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'warning: hey now!\n'
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

    def policy(i, so, se):
        return se if i.severity == 'error' else so

    with Inform(stream_policy=policy, prog_name=False):
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'warning: hey now!\n'
        assert captured[1] == ''
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

    with Inform(prog_name=False) as informer:
        informer.set_stream_policy('header')
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'warning: hey now!\n'
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

def test_exits(capsys):
    status = {}
    def callback():
        status['called'] = True

    with Inform(prog_name=False, termination_callback=callback) as inform:
        status = {}
        with pytest.raises(SystemExit) as exception:
            done()
        assert exception.value.args == (0,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate()
        assert exception.value.args == (0,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            error('hey now!')
            terminate()
        assert exception.value.args == (1,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == 'error: hey now!\n'
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate('hey now!')
        assert exception.value.args == (1,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'hey now!\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate(3)
        assert exception.value.args == (3,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            fatal('hey now!')
        assert exception.value.args == (1,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            try:
                raise Error('hey', when='now!')
            except Error as e:
                e.terminate()
        assert exception.value.args == (1,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            try:
                raise Error('hey', when='now!')
            except Error as e:
                e.terminate(template='{} {when}')
        assert exception.value.args == (1,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

        inform.error_status = 2
        inform.errors_accrued(reset=True)
        status = {}
        with pytest.raises(SystemExit) as exception:
            done()
        assert exception.value.args == (0,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate()
        assert exception.value.args == (0,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            error('hey now!')
            terminate()
        assert exception.value.args == (2,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == 'error: hey now!\n'
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate('hey now!')
        assert exception.value.args == (2,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'hey now!\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            terminate(3)
        assert exception.value.args == (3,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == ''

        status = {}
        with pytest.raises(SystemExit) as exception:
            fatal('hey now!')
        assert exception.value.args == (2,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            try:
                raise Error('hey', when='now!')
            except Error as e:
                e.terminate()
        assert exception.value.args == (2,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey\n'

        status = {}
        with pytest.raises(SystemExit) as exception:
            try:
                raise Error('hey', when='now!')
            except Error as e:
                e.terminate(template='{} {when}')
        assert exception.value.args == (2,)
        assert status.get('called') == True
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'


def test_error(capsys):
    with Inform(prog_name=False):
        try:
            raise Error('hey', when='now!')
        except Error as e:
            assert e.render() == 'hey'
            assert e.render(template='{} {when}') == 'hey now!'
            assert e.when == 'now!'
            assert e.args == ('hey',)
            assert e.kwargs == dict(when='now!')

            e.report()
            captured = capsys.readouterr()
            assert captured[0] == 'error: hey\n'
            assert captured[1] == ''

            e.report(template='{} {when}')
            captured = capsys.readouterr()
            assert captured[0] == 'error: hey now!\n'
            assert captured[1] == ''

            with pytest.raises(SystemExit) as exception:
                e.terminate()
            assert exception.value.args == (1,)
            captured = capsys.readouterr()
            assert captured[0] == ''
            assert captured[1] == 'error: hey\n'

            with pytest.raises(SystemExit) as exception:
                e.terminate(template='{} {when}')
            assert exception.value.args == (1,)
            captured = capsys.readouterr()
            assert captured[0] == ''
            assert captured[1] == 'error: hey now!\n'

            with pytest.raises(AttributeError) as exception:
                e.__xxx

def test_prog_name(capsys):
    prev_informer = get_informer()
    with Inform(prog_name='curly') as informer:
        assert informer.get_prog_name() == 'curly'
        assert informer.prog_name == 'curly'
        assert get_prog_name() == 'curly'
        assert get_informer() == informer
    assert get_informer() == prev_informer

    with Inform(argv=['curly']) as informer:
        assert informer.get_prog_name() == 'curly'
        assert informer.prog_name == 'curly'
        assert get_prog_name() == 'curly'
        assert get_informer() == informer
    assert get_informer() == prev_informer

def test_informer_attributes(capsys):
    with Inform(prog_name='curly', pizza=True) as informer:
        with pytest.raises(AttributeError) as exception:
            informer.__xxx
        assert informer.yep == None
        assert informer.prog_name == 'curly'
        assert informer.pizza == True

def test_logging(capsys):
    if sys.version[0] == '2':
        # io assumes unicode, which python2 does not provide by default
        # so use StringIO instead
        from StringIO import StringIO
        # Add support for with statement by monkeypatching
        StringIO.__enter__ = lambda self: self
        StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
    else:
        from io import StringIO

    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile, prog_name='dog', version='3v14') as msg:
            display('running test')

            assert msg.errors_accrued() == 0
            assert str(stdout.getvalue()) == 'running test\n'
            assert str(stderr.getvalue()) == ''
            logfile_text = logfile.getvalue()
            logfile_text_sum = str(logfile_text[:10]), str(logfile_text[-13:])
            assert logfile_text_sum == ('dog: versi', 'running test\n')
            assert '3v14' in logfile_text

            msg.set_logfile(False)
            error('oh no!')
            assert msg.errors_accrued() == 1
            assert str(stdout.getvalue()) == 'running test\ndog error: oh no!\n'
            assert str(stderr.getvalue()) == ''
            with pytest.raises(ValueError) as exception:
                logfile.getvalue()
            assert full_stop(exception.value) == 'I/O operation on closed file.'

def test_muting(capsys):
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hello\n'

    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=True):
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''

    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False) as informer:
        informer.suppress_output(True)
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''

    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=True) as informer:
        informer.suppress_output(False)
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hello\n'

    with Inform(prog_name=False, narrate=False, verbose=False, quiet=True):
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hello\n'


    with Inform(prog_name=False, narrate=True):
        narrate('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        comment('hello')
        captured = capsys.readouterr()
        assert captured[0] == ''
        display('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        output('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'hello\n'
        error('hello')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hello\n'

def test_rattle(capsys):
    # ProgressBar: real abscissa
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 1e-6
        step = 1e-9
        display('before')
        with ProgressBar(stop) as progress:
            value = 0
            while value <= stop:
                progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_company(capsys):
    # ProgressBar: real abscissa, reversed
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = -1e-6
        step = -1e-9
        display('before')
        with ProgressBar(stop) as progress:
            value = 0
            while value >= stop:
                progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_filling(capsys):
    # ProgressBar: real abscissa, interrupted
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 1e-6
        step = 1e-9
        display('before')
        with ProgressBar(stop, prefix='Progress: ', width=60) as progress:
            value = 0
            while value <= stop/2:
                progress.draw(value)
                value += step
            display('Hey now!')
            progress.draw(value)
            while value <= stop:
                progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            Progress: .....9.....8.....7.....6.....
            Hey now!
            Progress: .....9.....8.....7.....6.....5.....4.....3.....2.....1.....0
            after
        """).lstrip()

def test_being(capsys):
    # ProgressBar: real abscissa, interrupted by error
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 1e-6
        step = 1e-9
        display('before')
        try:
            with ProgressBar(stop) as progress:
                value = 0
                while value <= stop/2:
                    progress.draw(value)
                    value += step
                raise Error('Hey now!')
        except Error as e:
            e.report()
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......
            error: Hey now!
            after
        """).lstrip()

def test_deadbeat(capsys):
    # ProgressBar: log abscissa
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 1e-6
        start = 100e-9
        step = 1e-9
        display('before')
        with ProgressBar(stop, start=start, log=True) as progress:
            value = start
            while value <= stop:
                progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_lipstick(capsys):
    # ProgressBar: log abscissa, interrupted
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 1e-6
        start = 100e-9
        step = 1e-9
        display('before')
        with ProgressBar(stop, start=start, log=True) as progress:
            value = start
            while value <= stop/2:
                progress.draw(value)
                value += step
            progress.escape()
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5......4......
            after
        """).lstrip()

def test_stomp(capsys):
    # ProgressBar: log abscissa, reversed
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 100e-9
        start = 1e-6
        step = -1e-9
        display('before')
        with ProgressBar(stop=stop, start=start, log=True) as progress:
            value = start
            while value >= stop:
                progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_sherbet(capsys):
    # ProgressBar: iterator
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        for i in ProgressBar(range(50)):
            if i % 10 == 0:
                display('hello', i)
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            hello 0
            ......9.....
            hello 10
            ......9......8......7......
            hello 20
            ......9......8......7......6......5......
            hello 30
            ......9......8......7......6......5......4......3......
            hello 40
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_sherbet(capsys):
    # ProgressBar: integer
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        for i in ProgressBar(50):
            if i % 10 == 0:
                display('hello', i)
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            hello 0
            ......9......8
            hello 10
            ......9......8......7......6
            hello 20
            ......9......8......7......6......5......4
            hello 30
            ......9......8......7......6......5......4......3......2
            hello 40
            ......9......8......7......6......5......4......3......2......1......
            hello 50
            ......9......8......7......6......5......4......3......2......1......0
            after
        """).lstrip()

def test_prompter(capsys):
    # ProgressBar: empty iterator
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        for i in ProgressBar(range(0)):
            pass
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            after
        """).lstrip()

def test_paramedic(capsys):
    # ProgressBar: empty context manager
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        stop = 1e-6
        step = 1e-9
        value = 0
        with ProgressBar(stop, prefix='Progress: ') as progress:
            while value <= stop:
                # progress.draw(value)
                value += step
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            after
        """).lstrip()

def test_aerosol(capsys):
    # ProgressBar: empty context manager
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        for vs in ProgressBar([], prefix='nil: |', width=60):
            pass
        display('mid 1')
        for vs in ProgressBar([1], prefix='one: |', width=60):
            pass
        display('mid 2')
        for vs in ProgressBar([1,2], prefix='two: |', width=60):
            pass
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            mid 1
            one: |.....9.....8.....7.....6.....5.....4.....3.....2.....1.....0
            mid 2
            two: |.....9.....8.....7.....6.....5.....4.....3.....2.....1.....0
            after
        """).lstrip()

def test_employ(capsys):
    # ProgressBar: multiple escapes
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        stop = 10
        step = 1
        display('before')
        with ProgressBar(stop) as progress:
            value = 0
            while value <= stop:
                progress.draw(value)
                value += step
                if value > stop/2:
                    progress.escape()
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ......9......8......7......6......5
            after
        """).lstrip()

def test_orwell():
    # Info:
    from inform import Info

    class Orwell(Info):
        pass

    george = Orwell(peace='war', truth='lies')

    if sys.version_info >= (3,6):
        # argument sort order is unpredictable on earlier versions of python
        assert render(george) == "Orwell(peace='war', truth='lies')"
        assert repr(george) == "Orwell(peace='war', truth='lies')"
        assert str(george) == "Orwell(peace='war', truth='lies')"
    assert george.peace == 'war'
    assert george.truth == 'lies'
    assert george.happiness is None

def test_oblong():
    from inform import render_bar

    assert render_bar(-0.1, 25) == ''

    if sys.version_info < (3,):
        assert render_bar(1.1, 25) == '#########################'
        assert render_bar(0.11, 25) == '##='
        assert render_bar(0.66, 25) == '################-'
    else:
        assert render_bar(1.1, 25) == '█████████████████████████'
        assert render_bar(0.11, 25) == '██▊'
        assert render_bar(0.66, 25) == '████████████████▌'

