# Test Inform

# Imports {{{1
from inform import (
    Inform, InformantFactory, Error, codicil, display, done, error,
    errors_accrued, fatal, log, output, terminate, terminate_if_errors, warn,
    set_culprit, add_culprit, get_culprit, join_culprit
)
from contextlib import contextmanager
from textwrap import dedent
import sys
import re
import pytest
parametrize = pytest.mark.parametrize


if sys.version[0] == '2':
    # io assumes unicode, which python2 does not provide by default
    # so use StringIO instead
    from StringIO import StringIO
    # Add support for with statement by monkeypatching
    StringIO.__enter__ = lambda self: self
    StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
else:
    from io import StringIO

# Globals {{{1
sys.argv=['ack']
lorum_ipsum = dedent('''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
''').strip()

# Utilities {{{1
invokeExecutableRegex = r"(?<=ack: invoked as: )[^\n]+(?=\n)"
invokeTimeRegex = r"(?<=ack: log opened on )[^\n]+(?=\n)"
def strip(stringio):
    return stringio.getvalue().strip()

def log_strip(stringio):
    achieved = stringio.getvalue().strip()
    achieved = re.sub(invokeExecutableRegex, '<exe>', achieved)
    achieved = re.sub(invokeTimeRegex, '<date>', achieved)
    return achieved

# Helper classes and functions {{{1
@contextmanager
def messenger(*args, **kwargs):
    stdout = StringIO()
    stderr = StringIO()
    logfile = StringIO()
    with Inform(
        *args, stdout=stdout, stderr=stderr, prog_name=False, logfile=logfile,
        **kwargs
    ) as msg:
        yield msg, stdout, stderr, logfile
    stdout.close()
    stderr.close()
    logfile.close()


# Test cases {{{1
def test_grove():
    with messenger() as (msg, stdout, stderr, logfile):
        stimulus = 'hey now!'
        log(stimulus)
        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == ''
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=stimulus)

def test_billfold():
    with messenger() as (msg, stdout, stderr, logfile):
        display('hey now!', culprit=('yo', 'ho'))
        display('yep,\nYEP!', culprit='yep yep yep yep yep yep yep yep yep yep yep')
        expected = dedent('''
            yo, ho: hey now!
            yep yep yep yep yep yep yep yep yep yep yep:
                yep,
                YEP!
        ''').strip()

        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_wring():
    with messenger() as (msg, stdout, stderr, logfile):
        output('hey now!', flush=True)
        codicil('baby', 'bird', sep='\n')
        msg.flush_logfile()
        expected = dedent('''
            hey now!
            baby
            bird
        ''').strip()

        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

        try:
            terminate_if_errors()
            assert True
        except SystemExit:
            assert False

def test_fabricate():
    with messenger(hanging_indent=False) as (msg, stdout, stderr, logfile):
        error('hey now!')
        codicil('baby', 'bird', sep='\n')
        error('uh-huh\nuh-huh', culprit='yep yep yep yep yep yep yep yep yep yep yep'.split())
        expected = dedent('''
            error: hey now!
                baby
                bird
            error: yep, yep, yep, yep, yep, yep, yep, yep, yep, yep, yep:
                uh-huh
                uh-huh
        ''').strip()

        assert msg.errors_accrued() == 2
        assert errors_accrued(True) == 2
        assert msg.errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_cartwheel():
    with messenger() as (msg, stdout, stderr, logfile):
        warn('hey now!', culprit='yo')
        codicil('baby', 'bird', sep='\n')
        warn('uh-huh\nuh-huh', culprit='yep yep yep yep yep yep yep yep yep yep yep')
        expected = dedent('''
            warning: yo: hey now!
                baby
                bird
            warning: yep yep yep yep yep yep yep yep yep yep yep:
                uh-huh
                uh-huh
        ''').strip()

        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_vapor():
    with messenger() as (msg, stdout, stderr, logfile):
        report = InformantFactory(clone=display)
        stimulus = 'hey now!'
        report(stimulus)
        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == stimulus
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=stimulus)

def test_jumper():
    with messenger() as (msg, stdout, stderr, logfile):
        report = InformantFactory(clone=display, severity='forbidden', is_error=True)
        stimulus = 'hey now!'
        expected = 'forbidden: {}'.format(stimulus)
        report(stimulus)
        assert msg.errors_accrued() == 1
        assert errors_accrued() == 1
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

@parametrize(
    'culprits, culprits_as_str', [
        ('filename', 'filename: '),
        (0, '0: '),
        (('filename', 0), 'filename.0: '),
        (None, ''),
    ]
)
def test_culprits(culprits, culprits_as_str):
    with messenger(culprit_sep='.') as (msg, stdout, stderr, logfile):
        stimulus = 'hey now!'
        expected = 'warning: {}{}'.format(culprits_as_str, stimulus)
        warn(stimulus, culprit=culprits)
        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)


def test_pardon():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            terminate()
            assert False
        except SystemExit as e:
            assert e.args == (0,)

        try:
            raise Error('hey now!', culprit='nutz', extra='foo', codicil='putz')
            assert False
        except Error as err:
            assert err.get_message() == 'hey now!'
            assert err.get_culprit() == ('nutz',)
            assert err.get_codicil() == ('putz',)
            assert join_culprit(err.get_culprit()) == 'nutz'
            assert err.extra == 'foo'
            assert str(err) == 'nutz: hey now!'
            assert errors_accrued() == 0  # errors don't accrue until reported

        try:
            raise Error(
                'hey now!',
                culprit=('nutz',  'crunch'),
                extra='foo',
                codicil=('putz',  'toodle'),
            )
            assert False
        except Error as err:
            assert err.get_message() == 'hey now!'
            assert err.get_culprit() == ('nutz', 'crunch')
            assert err.get_codicil() == ('putz', 'toodle')
            assert join_culprit(err.get_culprit()) == 'nutz, crunch'
            assert err.extra == 'foo'
            assert str(err) == 'nutz, crunch: hey now!'
            assert err.get_message() == 'hey now!'
            assert err.get_message('{extra}, {}') == 'foo, hey now!'
            assert err.render() == 'nutz, crunch: hey now!'
            assert err.render('{extra}, {}') == 'nutz, crunch: foo, hey now!'
            assert errors_accrued() == 0  # errors don't accrue until reported
            try:
                err.terminate()
                assert False
            except SystemExit as e:
                assert e.args == (1,)

            try:
                done()
                assert False
            except SystemExit as e:
                assert e.args == (0,)

            try:
                rv = done(exit=False)
                assert rv == 0
            except SystemExit as e:
                assert False

            try:
                terminate()
                assert False
            except SystemExit as e:
                assert e.args == (1,)

            try:
                rv = terminate(exit=False)
                assert rv == 1
            except SystemExit as e:
                assert False

            try:
                rv = terminate(True, exit=False)
                assert rv == 1
            except SystemExit as e:
                assert False

            try:
                rv = terminate('fuxit', exit=False)
                assert rv == 1
            except SystemExit as e:
                assert False

            try:
                rv = terminate(6, exit=False)
                assert rv == 6
            except SystemExit as e:
                assert False

            try:
                terminate_if_errors()
                assert False
            except SystemExit as e:
                assert e.args == (1,)
                assert True

            try:
                rv = terminate_if_errors(exit=False)
                assert rv == 1
            except SystemExit as e:
                assert False

        try:
            raise Error('hey now', culprit=('nutz', 347))
            assert False
        except Error as err:
            assert err.get_message() == 'hey now'
            assert err.get_culprit() == ('nutz', 347)
            assert join_culprit(err.get_culprit()) == 'nutz, 347'
            assert join_culprit(err.get_culprit(66)) == '66, nutz, 347'
            assert join_culprit(err.get_culprit(('a', 'b'))) == 'a, b, nutz, 347'
            assert str(err) == 'nutz, 347: hey now'

def test_abase():
    with messenger() as (msg, stdout, stderr, logfile):
        class MyError0(Error):
            pass

        class MyError1(Error):
            template = 'bad mojo'

        class MyError2(Error):
            template = 'bad mojo: {}'

        try:
            raise MyError0('hey now!')
            assert False
        except Error as err:
            assert err.get_message() == 'hey now!'
            assert str(err) == 'hey now!'
            assert err.render() == 'hey now!'
            assert err.render(template='msg: {}') == 'msg: hey now!'

        try:
            raise MyError1('hey now!')
            assert False
        except Error as err:
            assert err.get_message() == 'bad mojo'
            assert err.render() == 'bad mojo'
            assert err.render(template='msg: {}') == 'msg: hey now!'

        try:
            raise MyError2('hey now!')
            assert False
        except Error as err:
            assert err.get_message() == 'bad mojo: hey now!'
            assert err.render() == 'bad mojo: hey now!'
            assert err.render(template='msg: {}') == 'msg: hey now!'

def test_possess():
    with messenger(stream_policy='header') as (msg, stdout, stderr, logfile):
        out = [
            'hey now!',
            'hey now!',
        ]
        err = [
            'Aiko aiko all day',
            'jockomo feeno na na nay',
            'jockomo feena nay.',
        ]
        display(*out)
        warn(*err, sep=', ')

        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == ' '.join(out)
        assert strip(stderr) == 'warning: ' + ', '.join(err)

def test_unbuckle():
    with messenger() as (msg, stdout, stderr, logfile):
        msg.set_stream_policy(lambda i, so, se: se if i.severity else so)
        out = [
            'hey now!',
            'hey now!',
        ]
        err = [
            'Aiko aiko all day',
            'jockomo feeno na na nay',
            'jockomo feena nay.',
        ]
        display(*out)
        warn(*err, sep=', ')

        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == ' '.join(out)
        assert strip(stderr) == 'warning: ' + ', '.join(err)

def test_franc():
    with messenger() as (msg, stdout, stderr, logfile):
        display('fuzzy', file=stdout, flush=True)
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == 'fuzzy'
        assert strip(stderr) == ''

def test_carbuncle():
    with messenger() as (msg, stdout, stderr, logfile):
        display('fuzzy', file=stdout)
        assert get_culprit() == ()
        assert get_culprit('x') == ('x',)
        assert get_culprit(('x', 'y')) == ('x', 'y')
        assert get_culprit(('x', 'y', 1)) == ('x', 'y', 1)
        with set_culprit('a'):
            assert get_culprit() == ('a',)
            assert get_culprit('x') == ('a', 'x')
            assert get_culprit(('x', 'y')) == ('a', 'x', 'y')
            with set_culprit('b'):
                assert get_culprit() == ('b',)
                assert get_culprit('x') == ('b', 'x')
                assert get_culprit(('x', 'y')) == ('b', 'x', 'y')
                with set_culprit('c'):
                    assert get_culprit() == ('c',)
                    assert get_culprit('x') == ('c', 'x')
                    assert get_culprit(('x', 'y')) == ('c', 'x', 'y')
        with add_culprit('a'):
            assert get_culprit() == ('a',)
            assert get_culprit('x') == ('a', 'x')
            assert get_culprit(('x', 'y')) == ('a', 'x', 'y')
            with add_culprit('b'):
                assert get_culprit() == ('a', 'b',)
                assert get_culprit('x') == ('a', 'b', 'x')
                assert get_culprit(('x', 'y')) == ('a', 'b', 'x', 'y')
                with add_culprit('c'):
                    assert get_culprit() == ('a', 'b', 'c',)
                    assert get_culprit('x') == ('a', 'b', 'c', 'x')
                    assert get_culprit(('x', 'y')) == ('a', 'b', 'c', 'x', 'y')
                    assert join_culprit(get_culprit((45, 99))) == 'a, b, c, 45, 99'

def test_guitar():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            raise Error('Hey now!')
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == 'error: Hey now!'
        assert strip(stderr) == ''

def test_tramp():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            raise Error('Hey now.', informant=display)
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == 'Hey now.'
        assert strip(stderr) == ''

def test_periphery():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            raise Error('Hey now.', informant=warn)
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == 'warning: Hey now.'
        assert strip(stderr) == ''

def test_cameraman():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            raise Error('Hey now.', informant=error)
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == 'error: Hey now.'
        assert strip(stderr) == ''

def test_roadway():
    with messenger() as (msg, stdout, stderr, logfile):
        with pytest.raises(Error) as exception:
            try:
                raise Error('Hey now!')
            except Error as e:
                e.reraise(culprit='bux')
        exception.value.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == 'error: bux: Hey now!'
        assert strip(stderr) == ''

def test_sedan():
    with messenger() as (msg, stdout, stderr, logfile):
        display('aaa bbb ccc')
        codicil('000 111 222')
        codicil('!!! @@@ ###')
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == dedent('''
            aaa bbb ccc
            000 111 222
            !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_fathead():
    with messenger() as (msg, stdout, stderr, logfile):
        display('aaa bbb ccc', codicil=('000 111 222', '!!! @@@ ###'))
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == dedent('''
            aaa bbb ccc
            000 111 222
            !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_ceilidh():
    with messenger() as (msg, stdout, stderr, logfile):
        warn('aaa bbb ccc')
        codicil('000 111 222')
        codicil('!!! @@@ ###')
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == dedent('''
            warning: aaa bbb ccc
                000 111 222
                !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_slice():
    with messenger() as (msg, stdout, stderr, logfile):
        warn('aaa bbb ccc', codicil=('000 111 222', '!!! @@@ ###'))
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == dedent('''
            warning: aaa bbb ccc
                000 111 222
                !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_toboggan():
    with messenger() as (msg, stdout, stderr, logfile):
        warn('aaa bbb ccc')
        codicil('000 111 222')
        codicil('!!! @@@ ###')
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == dedent('''
            warning: aaa bbb ccc
                000 111 222
                !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_showing():
    with messenger() as (msg, stdout, stderr, logfile):
        error('aaa bbb ccc', codicil=('000 111 222', '!!! @@@ ###'))
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == dedent('''
            error: aaa bbb ccc
                000 111 222
                !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_exact():
    with messenger() as (msg, stdout, stderr, logfile):
        error('aaa bbb ccc')
        codicil('000 111 222')
        codicil('!!! @@@ ###')
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == dedent('''
            error: aaa bbb ccc
                000 111 222
                !!! @@@ ###
        ''').strip()
        assert strip(stderr) == ''

def test_syllable():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            raise Error(
                'Hey now!', 'Hey now!',
                codicil=(
                    'Aiko aiko all day',
                    'jockomo feeno na na nay',
                    'jockomo feena nay'
                )
            )
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == dedent('''
            error: Hey now! Hey now!
                Aiko aiko all day
                jockomo feeno na na nay
                jockomo feena nay
        ''').strip()
        assert strip(stderr) == ''

def test_socialist():
    with messenger() as (msg, stdout, stderr, logfile):
        with pytest.raises(SystemExit) as exception:
            try:
                raise Error(
                    'Hey now!', 'Hey now!',
                    codicil=(
                        'Aiko aiko all day',
                        'jockomo feeno na na nay',
                        'jockomo feena nay'
                    ),
                    informant=fatal
                )
            except Error as e:
                e.report()
            assert msg.errors_accrued() == 1
            assert errors_accrued(True) == 1
            assert exception.value.args == (1,)
            assert strip(stdout) == dedent('''
                error: Hey now! Hey now!
                    Aiko aiko all day
                    jockomo feeno na na nay
                    jockomo feena nay
            ''').strip()
            assert strip(stderr) == ''

def test_crocodile():
    with messenger() as (msg, stdout, stderr, logfile):
        try:
            try:
                raise Error(
                    'Hey now!', 'Hey now!',
                    codicil=(
                        'Aiko aiko all day',
                        'jockomo feeno na na nay',
                        'jockomo feena nay'
                    )
                )
            except Error as e:
                e.reraise(culprit='I said')
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued(True) == 1
        assert strip(stdout) == dedent('''
            error: I said: Hey now! Hey now!
                Aiko aiko all day
                jockomo feeno na na nay
                jockomo feena nay
        ''').strip()
        assert strip(stderr) == ''

def test_envoy():
    with messenger() as (msg, stdout, stderr, logfile):
        expected = dedent('''
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
            minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat. Duis aute irure dolor in
            reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
            pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
            culpa qui officia deserunt mollit anim id est laborum.
        ''').strip()
        display(lorum_ipsum, wrap=True)
        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_jaguar():
    with messenger() as (msg, stdout, stderr, logfile):
        expected = dedent('''
            Lorem ipsum dolor sit amet, consectetur
            adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna
            aliqua. Ut enim ad minim veniam, quis
            nostrud exercitation ullamco laboris
            nisi ut aliquip ex ea commodo consequat.
            Duis aute irure dolor in reprehenderit
            in voluptate velit esse cillum dolore eu
            fugiat nulla pariatur. Excepteur sint
            occaecat cupidatat non proident, sunt in
            culpa qui officia deserunt mollit anim
            id est laborum.
        ''').strip()
        display(lorum_ipsum, wrap=40)
        assert msg.errors_accrued() == 0
        assert errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_birthmark():
    with messenger() as (msg, stdout, stderr, logfile):
        expected = dedent('''
            error:
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
                minim veniam, quis nostrud exercitation ullamco laboris nisi ut
                aliquip ex ea commodo consequat. Duis aute irure dolor in
                reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
                culpa qui officia deserunt mollit anim id est laborum.
        ''').strip()
        error(lorum_ipsum, wrap=True)
        assert msg.errors_accrued() == 1
        assert errors_accrued() == 1
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)


def test_currant():
    with messenger() as (msg, stdout, stderr, logfile):
        expected = dedent('''
            error:
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
                minim veniam, quis nostrud exercitation ullamco laboris nisi ut
                aliquip ex ea commodo consequat. Duis aute irure dolor in
                reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
                culpa qui officia deserunt mollit anim id est laborum.
        ''').strip()
        try:
            raise Error(lorum_ipsum, wrap=True)
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued() == 1
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)


def test_stripy():
    with messenger() as (msg, stdout, stderr, logfile):
        expected = dedent('''
            error: de Finibus Bonorum et Malorum
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
                minim veniam, quis nostrud exercitation ullamco laboris nisi ut
                aliquip ex ea commodo consequat. Duis aute irure dolor in
                reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
                culpa qui officia deserunt mollit anim id est laborum.
        ''').strip()
        try:
            raise Error('de Finibus Bonorum et Malorum', codicil=lorum_ipsum, wrap=True)
        except Error as e:
            e.report()
        assert msg.errors_accrued() == 1
        assert errors_accrued() == 1
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            ack: invoked as: <exe>
            ack: log opened on <date>
            {expected}
        ''').strip().format(expected=expected)

def test_capsys_out(capsys):
    output('hello world')
    cap = capsys.readouterr()
    assert cap.out == 'hello world\n'

def test_capsys_err(capsys):
    try:
        fatal('goodbye world')
    except SystemExit:
        pass
    cap = capsys.readouterr()
    assert 'goodbye world' in cap.err


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
