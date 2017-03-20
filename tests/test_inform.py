from inform import (
    Inform, Error, display, done, error, errors_accrued, log, output, terminate,
    terminate_if_errors, warn
)
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

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == 'yo, ho: hey now!\n'
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 3
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'yo, ho: hey now!'
    assert log_lines[2] == ''

def test_output():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile) as msg \
    :
        output('hey now!')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == 'hey now!\n'
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 3
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'hey now!'
    assert log_lines[2] == ''

    try:
        terminate_if_errors()
        assert True
    except SystemExit:
        assert False

def test_error():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile, prog_name=False) as msg \
    :
        error('hey now!')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued(True)
        num_errors3 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 1
    assert num_errors2 == 1
    assert num_errors3 == 0
    assert str(output_text) == 'error: hey now!\n'
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 3
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'error: hey now!'
    assert log_lines[2] == ''

def test_warn():
    with StringIO() as stdout, \
         StringIO() as stderr, \
         StringIO() as logfile, \
         Inform(stdout=stdout, stderr=stderr, logfile=logfile, prog_name=False) as msg \
    :
        warn('hey now!', culprit='yo')

        num_errors = msg.errors_accrued()
        num_errors2 = errors_accrued()
        output_text = stdout.getvalue()
        error_text = stderr.getvalue()
        logfile_text = logfile.getvalue()

    assert num_errors == 0
    assert num_errors2 == 0
    assert str(output_text) == 'warning: yo: hey now!\n'
    assert str(error_text) == ''
    log_lines = logfile_text.split('\n')
    assert len(log_lines) == 3
    assert log_lines[0].startswith('Invoked as')
    assert log_lines[1] == 'warning: yo: hey now!'
    assert log_lines[2] == ''

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
