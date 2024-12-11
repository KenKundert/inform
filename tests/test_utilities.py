# encoding: utf8

from inform import (
    Color, Error, Info, LoggingCache, columns, conjoin, did_you_mean, comment,
    cull, dedent, display, done, error, fatal, fmt, full_stop, indent, Inform,
    is_collection, is_iterable, is_mapping, is_str, join, get_prog_name,
    get_informer, narrate, os_error, output, plural, render, terminate,
    title_case, truth, warn, ddd, ppp, sss, vvv, ProgressBar, parse_range,
    format_range
)
from textwrap import dedent as tw_dedent
import sys
import pytest
from hypothesis import given
from hypothesis.strategies import iterables, integers

parametrize = pytest.mark.parametrize

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
    a, b, c = 'abc'
    ddd(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 32, tests.test_utilities.test_debug():
            'a'
            'b'
            'c'
    """).lstrip()

    ddd(a=a, b=b, c=c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 41, tests.test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    ppp(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 50, tests.test_utilities.test_debug(): a b c
    """).lstrip()

    vvv(a, b, c)
    captured = capsys.readouterr()
    assert captured[0] == dedent("""
        DEBUG: test_utilities.py, 56, tests.test_utilities.test_debug():
            a = 'a'
            b = 'b'
            c = 'c'
    """).lstrip()

    sss()
    captured = capsys.readouterr()
    assert captured[0].split('\n')[0] == "DEBUG: test_utilities.py, 65, tests.test_utilities.test_debug():"

    sss(ignore_exceptions=False)
    captured = capsys.readouterr()
    assert captured[0].split('\n')[0] == "DEBUG: test_utilities.py, 69, tests.test_utilities.test_debug()"

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

    items = [.14, 6.78, 9]
    assert conjoin(items, fmt='${:0.2f}', conj=None) == '$0.14, $6.78, $9.00'

    assert conjoin([], ' or ') == ''
    assert conjoin(['a'], ' or ') == 'a'

    assert conjoin(['a', 'b'], ' or ') == 'a or b'

    assert conjoin(['a', 'b', 'c']) == 'a, b and c'

    assert conjoin([10.1, 32.5, 16.9], fmt='${:0.2f}') == '$10.10, $32.50 and $16.90'

    if sys.version_info >= (3, 6):
        characters = dict(
            bob = 'bob@btca.com',
            ted = 'ted@btca.com',
            carol = 'carol@btca.com',
            alice = 'alice@btca.com',
        )
        assert conjoin(characters.items(), fmt='{0[0]} : <{0[1]}>', conj='\n', sep='\n') == dedent('''
            bob : <bob@btca.com>
            ted : <ted@btca.com>
            carol : <carol@btca.com>
            alice : <alice@btca.com>
        ''').strip()

    characters = [
        dict(name='bob', email='bob@btca.com'),
        dict(name='ted', email='ted@btca.com'),
        dict(name='carol', email='carol@btca.com'),
        dict(name='alice', email='alice@btca.com'),
    ]
    assert conjoin(characters, fmt="{0[name]} : <{0[email]}>", conj=' and\n', sep=',\n') == dedent('''
        bob : <bob@btca.com>,
        ted : <ted@btca.com>,
        carol : <carol@btca.com> and
        alice : <alice@btca.com>
    ''').strip()

    characters = [
        Info(name='bob', email='bob@btca.com'),
        Info(name='ted', email='ted@btca.com'),
        Info(name='carol', email='carol@btca.com'),
        Info(name='alice', email='alice@btca.com'),
    ]
    assert conjoin(characters, fmt='{0.name} : <{0.email}>', conj='; &\n', sep=';\n', end='.') == dedent('''
        bob : <bob@btca.com>;
        ted : <ted@btca.com>;
        carol : <carol@btca.com>; &
        alice : <alice@btca.com>.
    ''').strip()

    assert conjoin(characters, fmt=lambda a: a.render('{name} : <{email}>'), conj='\n', sep='\n') == dedent('''
        bob : <bob@btca.com>
        ted : <ted@btca.com>
        carol : <carol@btca.com>
        alice : <alice@btca.com>
    ''').strip()

def test_did_you_mean():
    assert did_you_mean('abc', ['bcd']) == 'bcd'
    assert did_you_mean('abc', ['cde']) == 'cde'
    assert did_you_mean('abc', ['bcd', 'cde']) == 'bcd'
    assert did_you_mean('abc', ['cde', 'bcd']) == 'bcd'

def test_title_case():
    cases = [(
        'CDC warns about "aggressive" rats as coronavirus shuts down restaurants',
        'CDC Warns About "Aggressive" Rats as Coronavirus Shuts Down Restaurants'
    ), (
        'L.A. County opens churches, stores, pools, drive-in theaters',
        'L.A. County Opens Churches, Stores, Pools, Drive-in Theaters'
    ), (
        'UConn senior accused of killing two men was looking for young woman',
        'UConn Senior Accused of Killing Two Men Was Looking for Young Woman'
    ), (
        'Giant asteroid that killed the dinosaurs slammed into Earth at ‘deadliest possible angle,’ study reveals',
        'Giant Asteroid That Killed the Dinosaurs Slammed Into Earth at ‘Deadliest Possible Angle,’ Study Reveals'
    ), (
        'Maintain given spacing: This is a test.  This is only a test.',
        'Maintain Given Spacing: This Is a Test.  This Is Only a Test.'
    )]
    for test, expected in cases:
        assert title_case(test) == expected

@pytest.mark.parametrize(
    'given, expected', [
            ('',        set()),
            (',',       set()),  # Extra commas are ok; they're not ambiguous.

            ('1',       {1}),
            ('1,1',     {1}),
            ('1-1',     {1}),

            ('1,2',     {1,2}),
            ('2,1',     {1,2}),
            ('1-2',     {1,2}),
            ('2-1',     {1,2}),

            ('1,3',     {1,3}),
            ('1,3,5',   {1,3,5}),
            ('1,3,5,6', {1,3,5,6}),
            ('1,3,5,7', {1,3,5,7}),
            ('1,3,5-7', {1,3,5,6,7}),

            ('1-3',     {1,2,3}),
            ('1-3,5',   {1,2,3,5}),
            ('1-3,5,6', {1,2,3,5,6}),
            ('1-3,5,7', {1,2,3,5,7}),
            ('1-3,5-7', {1,2,3,5,6,7}),
])
def test_parse_range_123(given, expected):
    assert parse_range(given) == expected

@pytest.mark.parametrize(
    'given, expected', [
            ('',        set()),
            (',',       set()),  # Extra commas are ok; they're not ambiguous.

            ('A',       {'A'}),
            ('A,A',     {'A'}),
            ('A-A',     {'A'}),

            ('A,B',     {'A','B'}),
            ('B,A',     {'A','B'}),
            ('A-B',     {'A','B'}),
            ('B-A',     {'A','B'}),

            ('A,C',     {'A','C'}),
            ('A,C,E',   {'A','C','E'}),
            ('A,C,E,F', {'A','C','E','F'}),
            ('A,C,E,G', {'A','C','E','G'}),
            ('A,C,E-G', {'A','C','E','F','G'}),

            ('A-C',     {'A','B','C'}),
            ('A-C,E',   {'A','B','C','E'}),
            ('A-C,E,F', {'A','B','C','E','F'}),
            ('A-C,E,G', {'A','B','C','E','G'}),
            ('A-C,E-G', {'A','B','C','E','F','G'}),
])
def test_parse_range_abc(given, expected):
    abc_range = lambda a, b: [chr(x) for x in range(ord(a), ord(b) + 1)]
    assert parse_range(given, cast=str, range=abc_range) == expected

@pytest.mark.parametrize(
    'given', [
        '-',
        '-1', # negative numbers can't be distinguished from malformed ranges.
        '1-1-1', 
        '?',
])
def test_parse_range_err(given):
    with pytest.raises(ValueError):
        parse_range(given)

@pytest.mark.parametrize(
    'given, expected', [
        ([],               ''),

        ([1],              '1'),
        ([1,1],            '1'),

        ([1,2],            '1,2'),
        ([2,1],            '1,2'),

        ([1,3],            '1,3'),
        ([3,1],            '1,3'),
        ([1,2,3],          '1-3'),
        ([3,1,2],          '1-3'),
        ([2,3,1],          '1-3'),

        ([1,3,5],          '1,3,5'),
        ([1,3,5,6],        '1,3,5,6'),
        ([1,3,5,6,7],      '1,3,5-7'),
        ([1,3,5,7],        '1,3,5,7'),

        ([1,2,3,5],        '1-3,5'),
        ([1,2,3,5,6],      '1-3,5,6'),
        ([1,2,3,5,6,7],    '1-3,5-7'),
        ([1,2,3,5,7],      '1-3,5,7'),

        ((1,),             '1'),
        ({1},              '1'),
        ({1:2},            '1'),
])
def test_format_range_123(given, expected):
    format_range(given) == expected

@pytest.mark.parametrize(
    'given, expected', [
        ([],            ''),

        ('A',           'A'),
        ('AA',          'A'),

        ('AB',          'A,B'),
        ('BA',          'A,B'),

        ('AC',          'A,C'),
        ('CA',          'A,C'),
        ('ABC',         'A-C'),
        ('CAB',         'A-C'),
        ('BCA',         'A-C'),

        ('ACE',         'A,C,E'),
        ('ACEF',        'A,C,E,F'),
        ('ACEFG',       'A,C,E-G'),
        ('ACEG',        'A,C,E,G'),

        ('ABCE',        'A-C,E'),
        ('ABCEF',       'A-C,E,F'),
        ('ABCEFG',      'A-C,E-G'),
        ('ABCEG',       'A-C,E,G'),

        (['A'],         'A'),
        (('A',),        'A'),
        ({'A'},         'A'),
        ({'A':'B'},     'A'),
])
def test_format_range_abc(given, expected):
    abc_diff = lambda a, b: ord(b) - ord(a)
    format_range(given, diff=abc_diff) == expected

@given(iterables(integers(min_value=0)))
def test_format_and_parse_range(x):
    assert parse_range(format_range(x)) == set(x._values)

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
    c=dedent('''\
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
    """\\
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
        'c': """\\
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
        'c': """\\
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
            'c': """\\
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
        'args': ('bbb',),
        'kwargs': {
            'child': {
                'args': ('aaa',),
                'kwargs': {'thisis': 'aaa'},
            },
            'thisis': 'bbb',
        },
    }
    ''').strip()
    assert render(bbb, sort=True) == bbb_expected_sorted

    ccc_expected_unsorted = dedent('''
    {
        'args': ('ccc',),
        'kwargs': {
            'thisis': 'ccc',
            'child': {
                'args': ('bbb',),
                'kwargs': {
                    'thisis': 'bbb',
                    'child': {
                        'args': ('aaa',),
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
        'args': ('ccc',),
        'kwargs': {
            'child': {
                'args': ('bbb',),
                'kwargs': {
                    'child': {
                        'args': ('aaa',),
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

    # Render must exit with its internal _sort and _level variables at None, 0
    # otherwise the sort and levels arguments will be retained from a previous
    # call.  This will happen if every call is balanced with a return.  To test
    # this, try rendering something that raises and error and see if it affects
    # the next call to render.
    try:
        render(fff, sort=True)
    except NotImplementedError:
        pass

    if sys.version_info >= (3, 6):
        assert render(ccc) == ccc_expected_unsorted

    assert render(ccc, sort=True) == ccc_expected_sorted


    # test ability to render inform-aware classes
    if sys.version_info >= (3, 6):
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
    assert '{:cart}'.format(plural(0)) == 'carts'
    assert '{:cart}'.format(plural(1)) == 'cart'
    assert '{:cart}'.format(plural(2)) == 'carts'
    assert '{:bush/es}'.format(plural(0)) == 'bushes'
    assert '{:bush/es}'.format(plural(1)) == 'bush'
    assert '{:bush/es}'.format(plural(2)) == 'bushes'
    assert '{:# cart}'.format(plural(0)) == '0 carts'
    assert '{:# cart}'.format(plural(1)) == '1 cart'
    assert '{:# cart}'.format(plural(2)) == '2 carts'
    assert '{:# bush/es}'.format(plural(0)) == '0 bushes'
    assert '{:# bush/es}'.format(plural(1)) == '1 bush'
    assert '{:# bush/es}'.format(plural(2)) == '2 bushes'
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

    assert '{:!cart/s}'.format(plural(0)) == 'cart'
    assert '{:!cart/s}'.format(plural(1)) == 'carts'
    assert '{:!cart/s}'.format(plural(2)) == 'cart'
    assert '{:!cart}'.format(plural(0)) == 'cart'
    assert '{:!cart}'.format(plural(1)) == 'carts'
    assert '{:!cart}'.format(plural(2)) == 'cart'
    assert '{:!# cart/s}'.format(plural(0)) == '0 cart'
    assert '{:!# cart/s}'.format(plural(1)) == '1 carts'
    assert '{:!# cart/s}'.format(plural(2)) == '2 cart'
    assert '{:!# cart}'.format(plural(0)) == '0 cart'
    assert '{:!# cart}'.format(plural(1)) == '1 carts'
    assert '{:!# cart}'.format(plural(2)) == '2 cart'
    assert '{:!/baby/babies}'.format(plural(0)) == 'baby'
    assert '{:!bab/y/ies}'.format(plural(0)) == 'baby'
    assert '{:!/baby/babies}'.format(plural(1)) == 'babies'
    assert '{:!bab/y/ies}'.format(plural(1)) == 'babies'
    assert '{:!/baby/babies}'.format(plural(2)) == 'baby'
    assert '{:!bab/y/ies}'.format(plural(2)) == 'baby'
    assert '{:!# /baby/babies}'.format(plural(0)) == '0 baby'
    assert '{:!# bab/y/ies}'.format(plural(0)) == '0 baby'
    assert '{:!# /baby/babies}'.format(plural(1)) == '1 babies'
    assert '{:!# bab/y/ies}'.format(plural(1)) == '1 babies'
    assert '{:!# /baby/babies}'.format(plural(2)) == '2 baby'
    assert '{:!# bab/y/ies}'.format(plural(2)) == '2 baby'
    assert '{:!# boy/s}'.format(plural(''.split())) == '0 boy'
    assert '{:!# boy/s}'.format(plural('carl'.split())) == '1 boys'
    assert '{:!# boy/s}'.format(plural('carl george'.split())) == '2 boy'
    assert '{:!# boy/s}'.format(plural(range(0))) == '0 boy'
    assert '{:!# boy/s}'.format(plural(range(1))) == '1 boys'
    assert '{:!# boy/s}'.format(plural(range(2))) == '2 boy'
    assert '{:~@ bush|es}'.format(plural(0, invert='~', num='@', slash='|')) == '0 bush'
    assert '{:~@ bush|es}'.format(plural(1, invert='~', num='@', slash='|')) == '1 bushes'
    assert '{:~@ bush|es}'.format(plural(2, invert='~', num='@', slash='|')) == '2 bush'
    assert plural(2, invert='~', num='@', slash='|').format('~@ cart|s') == '2 cart'

    bushes = plural(0, formatter='/a bush/# bushes/no bushes')
    assert bushes.format() == 'no bushes'
    assert f"{bushes}" == 'no bushes'
    assert str(bushes) == 'no bushes'
    assert repr(bushes) == 'plural(0)'
    bushes = plural(1, formatter='/a bush/# bushes/no bushes')
    assert bushes.format() == 'a bush'
    assert f"{bushes}" == 'a bush'
    assert str(bushes) == 'a bush'
    assert repr(bushes) == 'plural(1)'
    bushes = plural(2, formatter='/a bush/# bushes/no bushes')
    assert bushes.format() == '2 bushes'
    assert f"{bushes}" == '2 bushes'
    assert str(bushes) == '2 bushes'
    assert repr(bushes) == 'plural(2)'

    bushes = plural(0, formatter='/a bush/# bushes/no bushes')


def test_plural_fraction():
    from fractions import Fraction

    assert '{:# day}'.format(plural(Fraction(0,2))) == '0 days'
    assert '{:# day}'.format(plural(Fraction(1,2))) == '1/2 days'
    assert '{:# day}'.format(plural(Fraction(2,2))) == '1 day'
    assert '{:# day}'.format(plural(Fraction(3,2))) == '3/2 days'
    assert '{:# day}'.format(plural(Fraction(4,2))) == '2 days'
    assert '{:# ox/en}'.format(plural(Fraction(0,2))) == '0 oxen'
    assert '{:# ox/en}'.format(plural(Fraction(1,2))) == '1/2 oxen'
    assert '{:# ox/en}'.format(plural(Fraction(2,2))) == '1 ox'
    assert '{:# ox/en}'.format(plural(Fraction(3,2))) == '3/2 oxen'
    assert '{:# ox/en}'.format(plural(Fraction(4,2))) == '2 oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(Fraction(0,2))) == 'no oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(Fraction(1,2))) == '1/2 oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(Fraction(2,2))) == 'an ox'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(Fraction(3,2))) == '3/2 oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(Fraction(4,2))) == '2 oxen'

def test_plural_words():
    from num2words import num2words

    assert '{:# day}'.format(plural(0, render_num=num2words)) == 'zero days'
    assert '{:# day}'.format(plural(1, render_num=num2words)) == 'one day'
    assert '{:# day}'.format(plural(2, render_num=num2words)) == 'two days'
    assert '{:# ox/en}'.format(plural(0, render_num=num2words)) == 'zero oxen'
    assert '{:# ox/en}'.format(plural(1, render_num=num2words)) == 'one ox'
    assert '{:# ox/en}'.format(plural(2, render_num=num2words)) == 'two oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(0, render_num=num2words)) == 'no oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(1, render_num=num2words)) == 'an ox'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(2, render_num=num2words)) == 'two oxen'
    assert '{:/an ox/# oxen/no oxen}'.format(plural(42, render_num=num2words)) == 'forty-two oxen'

def test_plural_exception():
    with pytest.raises(ValueError) as exception:
        oxen = plural(42)
        f"{oxen:/an ox/# oxen/no oxen/}"
    assert str(exception.value) == "format specification has too many components."

def test_truth():
    assert f'{truth(True)}' == 'yes'
    assert f'{truth(False)}' == 'no'
    assert f'{truth(True):aye/no}' == 'aye'
    assert f'{truth(False):aye/no}' == 'no'
    t = truth(True, formatter='ja/nein')
    assert t.format() == 'ja'
    assert str(t) == 'ja'
    assert repr(t) == 'truth(True)'
    t = truth(False, formatter='ja/nein')
    assert t.format() == 'nein'
    assert str(t) == 'nein'
    assert repr(t) == 'truth(False)'

def test_full_stop():
    assert full_stop('hey now') == 'hey now.'
    assert full_stop('hey now.') == 'hey now.'
    assert full_stop('hey now?') == 'hey now?'
    assert full_stop('hey now!') == 'hey now!'
    assert full_stop('') == ''
    cases = '1, 2, 3, 5 7, 11 13 17.'.split()
    assert ' '.join(full_stop(c, end=',', allow=',.') for c in cases) == '1, 2, 3, 5, 7, 11, 13, 17.'

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
    assert Color('white', scheme='dark')('') == ''
    assert repr(Color('white', scheme='dark')) == "Color('white', scheme=dark)"

    assert Color('black', scheme='dark')('black') == '\x1b[0;30mblack\x1b[0m'
    assert Color('red', scheme='dark')('red') == '\x1b[0;31mred\x1b[0m'
    assert Color('green', scheme='dark')('green') == '\x1b[0;32mgreen\x1b[0m'
    assert Color('yellow', scheme='dark')('yellow') == '\x1b[0;33myellow\x1b[0m'
    assert Color('blue', scheme='dark')('blue') == '\x1b[0;34mblue\x1b[0m'
    assert Color('magenta', scheme='dark')('magenta') == '\x1b[0;35mmagenta\x1b[0m'
    assert Color('cyan', scheme='dark')('cyan') == '\x1b[0;36mcyan\x1b[0m'
    assert Color('white', scheme='dark')('white') == '\x1b[0;37mwhite\x1b[0m'
    assert Color('red', scheme='dark', enable=False)('disabled') == 'disabled'
    assert Color('cyan', scheme=None)('none') == 'none'
    assert Color('blue', scheme=None, enable=False)('none') == 'none'
    color =  Color('green', scheme='dark')
    color.enable = False
    assert color('disabled') == 'disabled'

    assert Color('black', scheme='light')('black') == '\x1b[1;30mblack\x1b[0m'
    assert Color('red', scheme='light')('red') == '\x1b[1;31mred\x1b[0m'
    assert Color('green', scheme='light')('green') == '\x1b[1;32mgreen\x1b[0m'
    assert Color('yellow', scheme='light')('yellow') == '\x1b[1;33myellow\x1b[0m'
    assert Color('blue', scheme='light')('blue') == '\x1b[1;34mblue\x1b[0m'
    assert Color('magenta', scheme='light')('magenta') == '\x1b[1;35mmagenta\x1b[0m'
    assert Color('cyan', scheme='light')('cyan') == '\x1b[1;36mcyan\x1b[0m'
    assert Color('white', scheme='light')('white') == '\x1b[1;37mwhite\x1b[0m'
    assert Color('yellow', scheme='light', enable=False)('disabled') == 'disabled'
    color =  Color('magenta', scheme='light')
    color.enable = False
    assert color('disabled') == 'disabled'

    Inform(colorscheme=None)
    assert Color('black')('black') == 'black'
    assert Color('white', scheme=True)('white') == 'white'
    Inform(colorscheme='dark')
    assert Color('black')('black') == '\x1b[0;30mblack\x1b[0m'
    assert Color('white', scheme=True)('white') == '\x1b[0;37mwhite\x1b[0m'
    Inform(colorscheme='light')
    assert Color('black')('black') == '\x1b[1;30mblack\x1b[0m'
    assert Color('white', scheme=True)('white') == '\x1b[1;37mwhite\x1b[0m'
    assert Color.strip_colors(Color('red')('red')) == 'red'

def test_join():
    assert join('a', 'b', 'c') == 'a b c'
    assert join('a', 'b', 'c', sep='-') == 'a-b-c'
    assert join('a', 'b', 'c', x='x', y='y', template='{}, x={x}') == 'a, x=x'
    assert join('Lorem\nipsum\ndolor', wrap=100) == 'Lorem ipsum dolor'
    c=dedent('''\
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
        display('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'hey now!\n'
        assert captured[1] == ''
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'warning: hey now!\n'
        assert captured[1] == ''
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'error: hey now!\n'
        assert captured[1] == ''

    with Inform(stream_policy='header', prog_name=False):
        display('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'hey now!\n'
        assert captured[1] == ''
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'warning: hey now!\n'
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

    with Inform(stream_policy='errors', prog_name=False):
        display('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'hey now!\n'
        assert captured[1] == ''
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == 'warning: hey now!\n'
        assert captured[1] == ''
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

    with Inform(stream_policy='all', prog_name=False):
        display('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'hey now!\n'
        warn('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'warning: hey now!\n'
        error('hey now!')
        captured = capsys.readouterr()
        assert captured[0] == ''
        assert captured[1] == 'error: hey now!\n'

    with pytest.raises(Error) as exception:
        Inform(stream_policy='toenail')
    assert str(exception.value) == "toenail: unknown stream policy."

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
        error("nutz")
        captured = capsys.readouterr()
        assert captured[0] == 'curly error: nutz\n'
    assert get_informer() == prev_informer

    with Inform(argv=['curly']) as informer:
        assert informer.get_prog_name() == 'curly'
        assert informer.prog_name == 'curly'
        assert get_prog_name() == 'curly'
        assert get_informer() == informer
        error("nutz")
        captured = capsys.readouterr()
        assert captured[0] == 'curly error: nutz\n'
    assert get_informer() == prev_informer

    with Inform(argv=['curly'], prog_name=True) as informer:
        assert informer.get_prog_name() == 'curly'
        assert informer.prog_name == 'curly'
        assert get_prog_name() == 'curly'
        assert get_informer() == informer
        error("nutz")
        captured = capsys.readouterr()
        assert captured[0] == 'curly error: nutz\n'
    assert get_informer() == prev_informer

    with Inform(argv=[], prog_name=True) as informer:
        assert informer.get_prog_name() == None
        assert informer.prog_name == None
        assert get_prog_name() == None
        assert get_informer() == informer
        error("nutz")
        captured = capsys.readouterr()
        assert captured[0] == 'error: nutz\n'
    assert get_informer() == prev_informer

    with Inform(argv=['curly'], prog_name=False) as informer:
        assert informer.get_prog_name() == 'curly'
        assert informer.prog_name == 'curly'
        assert get_prog_name() == 'curly'
        assert get_informer() == informer
        error("nutz")
        captured = capsys.readouterr()
        assert captured[0] == 'error: nutz\n'
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

def test_cached_logging(capsys):
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
         Inform(stdout=stdout, stderr=stderr, logfile=LoggingCache(), prog_name='dog', version='3v14') as msg:
            display('running test')
            msg.set_logfile(logfile)

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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
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
            Progress: ⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅
            Hey now!
            Progress: ⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅0
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8
            hello 10
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6
            hello 20
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4
            hello 30
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2
            hello 40
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
            after
        """).lstrip()

def test_world(capsys):
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8
            hello 10
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6
            hello 20
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4
            hello 30
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2
            hello 40
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅
            hello 50
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
            after
        """).lstrip()

def test_dockland(capsys):
    # ProgressBar: integer
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):
        display('before')
        for i in ProgressBar(50, width=-1):
            pass
        display('after')
        captured = capsys.readouterr()
        assert captured[0] == dedent("""
            before
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0
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
            one: |⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅0
            mid 2
            two: |⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅0
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
            ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5
            after
        """).lstrip()

def test_prophet(capsys):
    # ProgressBar: markers
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):

        repos = 'bias cp dac ldop pa ldop pa pbf topbias bias'.split()

        markers = dict(
            okay=('⋅', None),
            warn=('–', None),
            fail=('+', None),
            error=('×', "red")
        )
        with ProgressBar(len(repos), markers=markers) as progress:
            display('Progress:')
            for i in range(len(repos)):
                repo = repos[i]
                kind = 'error' if repo=='pbf' else 'fail' if repo=='ldop' else 'warn' if repo=='topbias' else 'okay'
                progress.draw(i+1, kind)

        captured = capsys.readouterr()
        assert captured[0] == dedent("""
        Progress:
        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7++++++6⋅⋅⋅⋅⋅⋅5++++++4⋅⋅⋅⋅⋅⋅3\x1b[0;31m××××××2\x1b[0m––––––1⋅⋅⋅⋅⋅⋅0
        """).lstrip()

def test_stylus(capsys):
    # ProgressBar: markers
    with Inform(prog_name=False, narrate=False, verbose=False, quiet=False, mute=False):

        # this test assure markers that were specified on a non-printing update
        # get retained on the next printing update.
        markers = dict(
            okay=('⋅', None),
            warn=('–', None),
            fail=('+', None),
            error=('×', None)
        )
        with ProgressBar(1000, markers=markers) as progress:
            display('Progress:')
            for i in range(1000):
                kind = 'error' if i==432 else 'fail' if i==506 else 'warn' if i==873 else 'okay'
                progress.draw(i+1, kind)

        captured = capsys.readouterr()
        assert captured[0] == dedent("""
        Progress:
        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅×⋅⋅⋅5+⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅–1⋅⋅⋅⋅⋅⋅0
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
    assert george.render(template='peace={peace}, truth={truth}') == 'peace=war, truth=lies'
    assert george.get('happiness') is None
    assert george.get('happiness', 'lost') == 'lost'

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


@parametrize('given', ['a', '\na', 'a\n', '\na\n', '\na\nb\n'])
def test_dedent_compatibility(given):
     assert dedent(given) == tw_dedent(given)


def test_render_tuples():
     assert render(()) == '()'
     assert render((0,)) == '(0,)'
     assert render((0,1)) == '(0, 1)'
     assert render((0,1,2)) == '(0, 1, 2)'


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
