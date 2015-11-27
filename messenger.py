# messenger -- utilities for communicating directly with the user

# License {{{1
# Copyright (C) 2014-16 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from __future__ import print_function
from copy import copy
import re
import os
import sys

# Globals {{{1
MESSENGER = None

# Messenger Utilities {{{1
# cull {{{2
def cull(collection, remove=None):
    if callable(remove):
        return [each for each in collection if not remove(each)]
    else:
        return [each for each in collection if each != remove]

# is_str {{{2
from six import string_types
def is_str(obj):
    return isinstance(obj, string_types)

# is_iterable {{{2
import collections
def is_iterable(obj):
    return isinstance(obj, collections.Iterable)

# is_collection {{{2
def is_collection(obj):
    return is_iterable(obj) and not is_str(obj)

# Color class {{{2
class Color:
    COLORS = ['black','red','green','yellow','blue','magenta','cyan','white'] 
        # The order of the above colors must match order of the standard 
        # terminal
    REGEX = re.compile('\033' + r'\[[01](;\d\d)?m')

    def __init__(self, color):
        self.color = color

    def __call__(self, text, scheme):
        if scheme and self.color:
            assert self.color in self.COLORS
            bright = 1 if scheme == 'light' else 0
            prefix = '\033[%s;3%dm' %(bright, self.COLORS.index(self.color))
            suffix = '\033[0m'
            return prefix + text + suffix
        else:
            return text

    @staticmethod
    def isTTY(stream=sys.stdout):
        try:
            return os.isatty(stream.fileno())
        except Exception:
            return False

    @classmethod
    def stripColors(cls, text):
        return cls.REGEX.sub('', text)


# User Utilities {{{1
# fmt {{{2
def fmt(message, *args, **kwargs):
    r"""
    Convert a message with embedded attributes to a string. The values for the 
    attributes can come from the argument list, as with ''.format(), or they may 
    come from the local scope (found by introspection).

    Examples:
    >>> from logger import fmt
    >>> s = 'str var'
    >>> d = {'msg': 'dict val'}
    >>> class Class:
    ...     a = 'cls attr'

    >>> print(fmt("by order: {0}, {1[msg]}, {2.a}.", s, d, Class))
    by order: str var, dict val, cls attr.
    >>> print(fmt("by name: {S}, {D[msg]}, {C.a}.", S=s, D=d, C=Class))
    by name: str var, dict val, cls attr.

    The following works, but does not work with doctests
    # >>> print(fmt("by magic: {s}, {d[msg]}, {c.a}."))
    # by magic: str var, dict val, cls attr.
    """
    import inspect

    # Inspect variables from the source frame.
    level = kwargs.pop('_level', 1)
    frame = inspect.stack()[-level][0]

    # Collect all the variables in the scope of the calling code, so they 
    # can be substituted into the message.
    attrs = {}
    attrs.update(frame.f_globals)
    attrs.update(frame.f_locals)
    attrs.update(kwargs)

    return message.format(*args, **attrs)

# os_error {{{2
# Generates a reasonable error message for an operating system error
def os_error(err):
    if err.filename:
        return "%s: %s." % (err.filename, err.strerror)
    else:
        return "%s." % (err.strerror)

# conjoin {{{2
# Like join, but supports conjunction
def conjoin(iterable, conj=' and ', sep=', '):
    """
    Conjunction Join
    Return the list joined into a string, where conj is used to join the last
    two items in the list, and sep is used to join the others.

    Examples:
    >>> conjoin([], ' or ')
    ''
    >>> conjoin(['a'], ' or ')
    'a'
    >>> conjoin(['a', 'b'], ' or ')
    'a or b'
    >>> conjoin(['a', 'b', 'c'])
    'a, b and c'
    """
    lst = list(iterable)
    if conj != None and len(lst) > 1:
        lst = lst[0:-2] + [lst[-2] + conj + lst[-1]]
    return sep.join(lst)

# plural {{{2
def plural(count, singular, plural=None):
    if plural is None:
        plural = singular + 's'
    if is_iterable(count):
        return singular if len(count) == 1 else plural
    else:
        return singular if count == 1 else plural

# MessengerGenerator class {{{1
class MessengerGenerator:
    def __init__(
        self,
        severity=None,
            # messages with severities get headers and severity acts as label
        is_error=False,
            # is counted as an error
        log=True,
            # send to the log file, may be a boolean or a function that accepts 
            # the messenger as an argument and returns a boolean
        output=True,
            # send to the output stream, may be a boolean or a function that 
            # accepts the messenger as an argument and returns a boolean
        terminate=False,
            # terminate the program, exit status is the value of the terminate 
            # unless terminate==True, in which case 1 is returned if an error 
            # occurred and 0 otherwise
        message_color=None,
            # color used to display the message
        header_color=None,
            # color used to display the header, if one is produced
    ):
        self.severity = severity
        self.is_error = is_error
        self.log = log
        self.output = output
        self.terminate = terminate
        self.message_color = Color(message_color)
        self.header_color = Color(header_color)
        self.stream = sys.stderr if self.terminate else sys.stdout

    def __call__(self, *args, **kwargs):
        MESSENGER.report(args, kwargs, self)

    def produce_output(self, messenger):
        return self.write_output(messenger) or self.write_logfile(messenger)

    def write_output(self, messenger):
        try:
            return self.output(messenger)
        except TypeError:
            return self.output

    def write_logfile(self, messenger):
        try:
            return self.log(messenger)
        except TypeError:
            return self.log


# Messengers {{{1
log = MessengerGenerator(
    output=False,
    log=True,
)
comment = MessengerGenerator(
    output=lambda messenger: messenger.verbose and not messenger.mute,
    log=True,
    message_color='cyan',
)
narrate = MessengerGenerator(
    output=lambda messenger: messenger.narrate and not messenger.mute,
    log=True,
    message_color='blue',
)
display = MessengerGenerator(
    output=lambda messenger: not messenger.quiet and not messenger.mute,
    log=True,
)
output = MessengerGenerator(
    output=lambda messenger: not messenger.mute,
    log=True,
)
debug = MessengerGenerator(
    severity='DEBUG',
    output=True,
    log=True,
    header_color='magenta',
)
warn = MessengerGenerator(
    severity='warning',
    header_color='yellow',
    output=lambda messenger: not messenger.quiet and not messenger.mute,
    log=True,
)
error = MessengerGenerator(
    severity='error',
    is_error=True,
    header_color='red',
    output=lambda messenger: not messenger.mute,
    log=True,
)
fatal = MessengerGenerator(
    severity='error',
    is_error=True,
    terminate=1,
    header_color='red',
    output=lambda messenger: not messenger.mute,
    log=True,
)
panic = MessengerGenerator(
    severity='internal error (please report)',
    is_error=True,
    terminate=3,
    header_color='red',
    output=True,
    log=True,
)

# Messenger class {{{1
class Messenger:
    """Messenger

    Handles all user messaging.  Copies all messages to the logfile while 
    sending most to standard out as well.
    """

    # constructor {{{2
    def __init__(
        self,
        mute=False,
        quiet=False,
        verbose=False,
        narrate=False,
        logfile=None,
        prog_name=None,
        argv=None,
        version=None,
        termination_callback=None,
        colorscheme='dark',
        stdout=None,
        stderr=None,
        **kwargs
    ):
        """
        Arguments:
        mute (bool)
            All output is suppressed (it is still logged).
        quiet (bool)
            Normal output is suppressed (it is still logged).
        verbose (bool)
            Comments are output to user, normally they are just logged.
        narrate (bool)
            Narration is output to user, normally it is just logged.
        logfile (string or stream)
            Path to logfile. By default, .<prog_name>.log is used. May also 
            pass an open stream. Pass False if no logfile is desired.
        prog_name (string)
            Program name By default, basename(argv[0]) is used. Use False to 
            indicate that program name should not be added to message headers.
        argv (list of strings)
            System command line arguments (logged). By default, sys.argv is 
            used.
        version (string)
            program version (logged)
        termination_callback (func)
            A function that is called at program termination. The list of 
            recorded messages is provided as the only argument.
        colorscheme (None, 'light', or 'dark')
            Color scheme to use. None indicates that messages should not be 
            colorized. Colors are not used if desired output stream is not 
            a TTY.
        stdout (stream)
            Messages are sent here by default. Generally used for testing. If 
            not given, sys.stdout is used.
        stderr (stream)
            Termination messages are sent here by default. Generally used for 
            testing.  If not given, sys.stderr is used.
        **kwargs
            Any additional keyword arguments are made attributes that are 
            ignored by Messenger, but may be accessed by the messengers.
        """
        self.errors = 0
        self.termination_callback = termination_callback
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr
        self.__dict__.update(kwargs)

        # make verbosity flags consistent
        self.mute = mute
        self.quiet = quiet
        if quiet:
            self.verbose = self.narrate = False
        else:
            self.verbose = verbose
            self.narrate = narrate

        # determine program name
        if not argv:
            argv = sys.argv
        self.prog_name = prog_name
        if argv and not prog_name:
            self.prog_name = os.path.basename(argv[0])
        if prog_name is False:
            self.prog_name = None

        # open logfile if is given as a string
        if is_str(logfile) or logfile is None:
            if self.prog_name and not logfile:
                logfile = '.%s.log' % self.prog_name
            if logfile:
                try:
                    logfile = open(logfile, 'w')
                except (IOError, OSError) as err:
                    print(os_error(err), file=sys.stderr)
        self.logfile = logfile

        # Save the color scheme
        assert colorscheme in [None, 'light', 'dark']
        self.colorscheme = colorscheme

        # Activate the actions
        global MESSENGER
        MESSENGER = self

        # write header to log file
        if version:
            self.log("%s version %s" % (self.prog_name, version))
        try:
            from datetime import datetime
            now = datetime.now().strftime(
                " on %A, %d %B %Y at %I:%M:%S %p")
        except:
            now = ""
        log("Invoked as '%s'%s." % (' '.join(argv), now))

    # __getattr__ {{{2
    def __getattr__(self, name):
        return self.__dict__.get(name)

    # report {{{2
    def report(self, args, kwargs, action):
        if action.is_error:
            self.errors += 1
        prefix = kwargs.get('prefix')
        if action.produce_output(self):
            options = self._get_print_options(kwargs, action)
            message = self._render_message(args, kwargs)
            header = self._render_header(action, prefix)
            msgcolor = action.message_color
            hdrcolor = action.header_color
            if action.write_output(self):
                cs = self.colorscheme if Color.isTTY(options['file']) else None
                if header:
                    print(
                        hdrcolor(header, cs) + msgcolor(message, cs),
                        **options
                    )
                else:
                    print(msgcolor(message, cs), **options)
            if action.write_logfile(self) and self.logfile:
                options['file'] = self.logfile
                print('%s%s' % (header, message), **options)
        if action.terminate is not False:
            self.terminate(status=action.terminate)

    # _get_print_options {{{2
    def _get_print_options(self, kwargs, action):
        opts= {
            'file': kwargs.get(
                'file',
                self.stderr if action.terminate else self.stdout
            ),
        }
        # do not add flush needlessly because it is not supported in python2
        if 'flush' in kwargs:
            opts['flush'] = kwargs.get('flush')
        return opts

    # _render_message {{{2
    @staticmethod
    def _render_message(args, kwargs):
        return kwargs.get('sep', ' ').join(str(arg) for arg in args)

    # _render_header {{{2
    def _render_header(self, action, prefix):
        if action.severity:
            if self.prog_name:
                header = '%s %s: ' % (self.prog_name, action.severity)
            else:
                header = '%s: ' % action.severity

            if prefix:
                if is_collection(prefix):
                    prefix = '.'.join(str(c) for c in prefix)
                header += str(prefix) + ': '
            return header
        return ''

    # done {{{2
    def done(self):
        "Normal termination"
        if self.termination_callback:                                                                                  
            self.termination_callback()
        log('%s: terminates normally.' % self.prog_name)
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        sys.exit()

    # terminate {{{2
    def terminate(self, status=None):
        """Abnormal termination

        status codes:
            None: return 1 if errors occurred and 0 otherwise
            0: success
            1: unexpected error
            2: invalid invocation
            3: panic
        """
        if status is None or status is True:
            status = 1 if self.errors_accrued() else 0;
        assert 0 <= status and status < 128
        if self.termination_callback:                                                                                  
            self.termination_callback()
        log('%s: terminates with status %s.' % (self.prog_name, status))
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        sys.exit(status)

    # terminate_if_errors {{{2
    def terminate_if_errors(self, status=1):
        if self.errors:
            self.terminate(status)

    # errors_accrued {{{2
    def errors_accrued(self):
        # returns number of errors that have accrued
        return self.errors

    # disconnect {{{2
    def disconnect(self):
        "Disconnect messenger"
        if self.logfile:
            self.logfile.flush()
        global MESSENGER
        MESSENGER = None

    # __enter__ {{{2
    def __enter__(self):
        return self

    # __exit__ {{{2
    def __exit__(self, type, value, traceback):
        self.disconnect()

# Direct access to class methods {{{2
# done {{{3
def done():
    MESSENGER.done()

# terminate {{{3
def terminate(status=True):
    MESSENGER.terminate(status)

# terminate_if_errors {{{3
def terminate_if_errors(status=1):
    MESSENGER.terminate_if_errors(status)

# errors_accrued {{{3
def errors_accrued():
    return MESSENGER.errors_accrued()

# Instantiate default messenger {{{1
MESSENGER = Messenger()

# Exceptions {{{1
# UserError {{{2
class UserError(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __str__(self):
        return kwargs.get('sep', ' ').join(str(a) for a in self.args)
    def report(self):
        error(*self.args, **self.kwargs)
