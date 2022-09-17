# Test Inform debug functions

try:                 # python3
    import builtins
except ImportError:  # python2
    import __builtin__ as builtins

# Imports {{{1
from inform import Inform, aaa, ccc, ddd, ppp, sss, vvv
from textwrap import dedent
import sys


# Test cases {{{1
def test_anglicize(capsys):
    Inform(colorscheme=None, prog_name=False)
    ppp()
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 17, tests.test_debug.test_anglicize()
    ''').lstrip()

def test_grouch(capsys):
    Inform(colorscheme=None, prog_name=False)
    a = 0
    b = 'b'
    ppp('hey now!', a, b)
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 27, tests.test_debug.test_grouch(): hey now! 0 b
    ''').lstrip()

def test_salver(capsys):
    Inform(colorscheme=None, prog_name=False)
    if sys.version_info >= (3,6):
        a = 0
        b = 'b'
        c = [a, b]
        d = {a, b}
        e = {a:b}
        ddd('hey now!', a, b, c, d, e)
        out, err = capsys.readouterr()
        assert out == dedent('''
            DEBUG: test_debug.py, 41, tests.test_debug.test_salver():
                'hey now!'
                0
                'b'
                [0, 'b']
                {0, 'b'}
                {0: 'b'}
        ''').lstrip()

def test_daiquiri(capsys):
    Inform(colorscheme=None, prog_name=False)
    if sys.version_info >= (3,6):
        a = 0
        b = 'b'
        c = [a, b]
        d = {a, b}
        e = {a:b}
        ddd(s='hey now!', a=a, b=b, c=c, d=d, e=e)
        out, err = capsys.readouterr()
        assert out == dedent('''
            DEBUG: test_debug.py, 61, tests.test_debug.test_daiquiri():
                a = 0
                b = 'b'
                c = [0, 'b']
                d = {0, 'b'}
                e = {0: 'b'}
                s = 'hey now!'
        ''').lstrip()

class Info:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        ddd(self=self, **kwargs)

def test_prude(capsys):
    Inform(colorscheme=None, prog_name=False)
    Info(email='ted@ledbelly.com')
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 76, tests.test_debug.Info.__init__():
            email = 'ted@ledbelly.com'
            self = Info object containing {'email': 'ted@ledbelly.com'}
    ''').lstrip()

def test_update(capsys):
    Inform(colorscheme=None, prog_name=False)
    if sys.version_info >= (3,6):
        a = 0
        b = 'b'
        c = [a, b]
        d = {a, b}
        e = {a:b}
        vvv()
        out, err = capsys.readouterr()
        out = '\n'.join(l for l in out.split('\n') if 'capsys' not in l)
        assert out == dedent('''
            DEBUG: test_debug.py, 96, tests.test_debug.test_update():
                a = 0
                b = 'b'
                c = [0, 'b']
                d = {0, 'b'}
                e = {0: 'b'}
        ''').lstrip()

def test_shear(capsys):
    Inform(colorscheme=None, prog_name=False)
    if sys.version_info >= (3,6):
        a = 0
        b = 'b'
        c = [a, b]
        d = {a, b}
        e = {a:b}
        vvv(a, b, c, d, e)
        out, err = capsys.readouterr()
        assert out == dedent('''
            DEBUG: test_debug.py, 116, tests.test_debug.test_shear():
                a = 0
                b = 'b'
                c = [0, 'b']
                d = {0, 'b'}
                e = {0: 'b'}
        ''').lstrip()

def test_prostrate(capsys):
    Inform(colorscheme=None, prog_name=False)
    sss()
    out, err = capsys.readouterr()
    out = out.strip().split('\n')
    assert out[0] == 'DEBUG: test_debug.py, 129, tests.test_debug.test_prostrate():'
    assert out[-2][-50:] == "tests/test_debug.py', line 129, in test_prostrate,"
    assert out[-1] == '        sss()'

def test_rubber(capsys):
    Inform(colorscheme=None, prog_name=False)
    a = aaa('a')
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 138, tests.test_debug.test_rubber(): 'a'
    ''').lstrip()
    assert a == 'a'

    b = aaa(b = 'b')
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 145, tests.test_debug.test_rubber(): b: 'b'
    ''').lstrip()
    assert b == 'b'

def test_bartender(capsys):
    Inform(colorscheme=None, prog_name=False)
    b = 'b'
    ret = aaa(b)
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 155, tests.test_debug.test_bartender(): 'b'
    ''').lstrip()
    assert ret == 'b'

def test_scene(capsys):
    msg = Inform(colorscheme=None, prog_name=False)
    ccc(msg)
    out, err = capsys.readouterr()
    assert out == dedent('''
        DEBUG: test_debug.py, 164, tests.test_debug.test_scene(): Inform
    ''').lstrip()


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
