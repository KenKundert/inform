#!/usr/bin/env python

# Test Inform

# Imports {{{1
from inform import (
    Inform, Error, codicil, display, done, error, errors_accrued, log, output,
    terminate, terminate_if_errors, warn
)
from contextlib import contextmanager
from textwrap import dedent
import sys
import re

if sys.version[0] == '2':
    # io assumes unicode, which python2 does not provide by default
    # so use StringIO instead
    from StringIO import StringIO
    # Add support for with statement by monkeypatching
    StringIO.__enter__ = lambda self: self
    StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
else:
    from io import StringIO

# Utilities {{{1
invokeTimeRegex = r"(?<=Invoked as )'.*' on .*(?=\.)"
def strip(stringio):
    return stringio.getvalue().strip()

def log_strip(stringio):
    achieved = stringio.getvalue().strip()
    achieved = re.sub(invokeTimeRegex, '<exe> on <date>', achieved)
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
            Invoked as <exe> on <date>.
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
            Invoked as <exe> on <date>.
            {expected}
        ''').strip().format(expected=expected)

def test_wring():
    with messenger() as (msg, stdout, stderr, logfile):
        output('hey now!')
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
            Invoked as <exe> on <date>.
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
        error('uh-huh\nuh-huh', culprit='yep yep yep yep yep yep yep yep yep yep yep')
        expected = dedent('''
            error: hey now!
                baby
                bird
            error: yep yep yep yep yep yep yep yep yep yep yep:
                uh-huh
                uh-huh
        ''').strip()

        assert msg.errors_accrued() == 2
        assert errors_accrued(True) == 2
        assert msg.errors_accrued() == 0
        assert strip(stdout) == expected
        assert strip(stderr) == ''
        assert log_strip(logfile) == dedent('''
            Invoked as <exe> on <date>.
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
            Invoked as <exe> on <date>.
            {expected}
        ''').strip().format(expected=expected)

def test_pardon():
    with messenger() as (msg, stdout, stderr, logfile):
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
            assert err.get_message() == 'hey now!'
            assert err.get_message('{extra}, {}') == 'foo, hey now!'
            assert err.render() == 'nutz, crunch: hey now!'
            assert err.render('{extra}, {}') == 'nutz, crunch: foo, hey now!'
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
        display('fuzzy', file=stdout)
        assert msg.errors_accrued() == 0
        assert errors_accrued(True) == 0
        assert strip(stdout) == 'fuzzy'
        assert strip(stderr) == ''
