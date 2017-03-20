from inform import (
    Inform, Error, codicil, display, done, error, errors_accrued, log, output,
    terminate, terminate_if_errors, warn
)
from textwrap import dedent
import sys

if sys.version[0] == '2':
    # io assumes unicode, which python2 does not provide by default
    # so use StringIO instead
    from StringIO import StringIO
    # Add support for with statement by monkeypatching
    StringIO.__enter__ = lambda self: self
    StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
else:
    from io import StringIO

def test_log():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile) as msg \
    :
        log('hey now!')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == ''
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 3
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'hey now!'
    assert log_lines[2] == ''

def test_display():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile) as msg \
    :
        display('hey now!', culprit=('yo', 'ho'))
        display('yep,\nYEP!', culprit='yep yep yep yep yep yep yep yep yep yep yep')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == dedent('''
        yo, ho: hey now!
        yep yep yep yep yep yep yep yep yep yep yep:
            yep,
                YEP!
    ''').lstrip()
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 6
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'yo, ho: hey now!'
    assert log_lines[2] == 'yep yep yep yep yep yep yep yep yep yep yep:'
    assert log_lines[3] == '    yep,'
    assert log_lines[4] == '        YEP!'
    assert log_lines[5] == ''

def test_output():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile) as msg \
    :
        output('hey now!')
        codicil('baby', 'bird', sep='\n')
        msg.flush_logfile()

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == 'hey now!\nbaby\nbird\n'
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 5
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'hey now!'
    assert log_lines[2] == 'baby'
    assert log_lines[3] == 'bird'
    assert log_lines[4] == ''

    try:
        terminate_if_errors()
        assert True
    except SystemExit:
        assert False

def test_error():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(
            stdout=stdout, stderr=stderr, logfile=logfile, prog_name=False,
            hanging_indent=False
         ) as msg \
    :
        error('hey now!')
        codicil('baby', 'bird', sep='\n')
        error('yep,\nYEP!', culprit='yep yep yep yep yep yep yep yep yep yep yep')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued(True)
        num_errors3 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 2
    assert num_errors2 == 2
    assert num_errors3 == 0
    assert str(output_text) == dedent('''
        error: hey now!
            baby
            bird
        error:
            yep yep yep yep yep yep yep yep yep yep yep:
                yep,
                YEP!
    ''').lstrip()
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 9
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'error: hey now!'
    assert log_lines[2] == '    baby'
    assert log_lines[3] == '    bird'
    assert log_lines[4] == 'error:'
    assert log_lines[5] == '    yep yep yep yep yep yep yep yep yep yep yep:'
    assert log_lines[6] == '        yep,'
    assert log_lines[7] == '        YEP!'
    assert log_lines[8] == ''

def test_warn():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(
            stdout=stdout, stderr=stderr, logfile=logfile, prog_name=False
        ) as msg \
    :
        warn('hey now!', culprit='yo')
        codicil('baby', 'bird', sep='\n')
        warn('yep,\nYEP!', culprit='yep yep yep yep yep yep yep yep yep yep yep')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == dedent('''
        warning: yo: hey now!
            baby
                bird
        warning:
            yep yep yep yep yep yep yep yep yep yep yep:
                yep,
                    YEP!
    ''').lstrip()
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 9
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'warning: yo: hey now!'
    assert log_lines[2] == '    baby'
    assert log_lines[3] == '        bird'
    assert log_lines[4] == 'warning:'
    assert log_lines[5] == '    yep yep yep yep yep yep yep yep yep yep yep:'
    assert log_lines[6] == '        yep,'
    assert log_lines[7] == '            YEP!'
    assert log_lines[8] == ''

def test_Error():
    try:
        raise Error('hey now!', culprit='nutz', extra='foo')
        assert False
    except Error as err:
        assert err.get_message() == 'hey now!'
        assert err.get_culprit() == 'nutz'
        assert err.extra == 'foo'
        assert str(err) == 'nutz: hey now!'
        assert errors_accrued() == 0  # errors don't accrue until reported

    try:
        raise Error('hey now!', culprit=('nutz',  'crunch'), extra='foo')
        assert False
    except Error as err:
        assert err.get_message() == 'hey now!'
        assert err.get_culprit() == 'nutz, crunch'
        assert err.extra == 'foo'
        assert str(err) == 'nutz, crunch: hey now!'
        assert errors_accrued() == 0  # errors don't accrue until reported
        try:
            err.terminate()
            assert False
        except SystemExit:
            assert True

        try:
            done()
            assert False
        except SystemExit:
            assert True

        try:
            terminate()
            assert False
        except SystemExit:
            assert True

        try:
            terminate_if_errors()
            assert False
        except SystemExit:
            assert True
