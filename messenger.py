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
# indent {{{2
def indent(text, leader = '   '):
    r"""{
    Add indentation.

    Examples:
    >>> from logger import indent
    >>> print(indent('Hello\nWorld!', '    '))
        Hello
        World!

    }"""
    return '\n'.join([
        leader+line if line else line for line in text.split('\n')
    ])

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
        is_error=False,
        log=True,
        output=True,
        terminate=False,
        is_continuation=False,
        message_color=None,
        header_color=None,
    ):
        """
        Arguments:
        severity (string)
            Messages with severities get headers; the severity acts as label.
            If the message has a header and the message text contains 
            a newline, then the text is indented and placed on the line that 
            follows the header.
        is_error (bool)
            Message is counted as an error.
        log (bool)
            Send message to the log file.  May be a boolean or a function that 
            accepts the messenger as an argument and returns a boolean.
        output (bool)
            Send message to the output stream.  May be a boolean or a function 
            that accepts the messenger as an argument and returns a boolean.
        terminate (bool or integer)
            Terminate the program.  Exit status is the value of terminate 
            unless terminate==True, in which case 1 is returned if an error 
            occurred and 0 otherwise.
        is_continuation (bool)
            This message is a continuation of the previous message.  It will 
            use the properties of the previous message (output, log, message 
            color, etc) and if the previous message had a header, that header 
            is not output and instead the message is indented.
        message_color (string)
            Color used to display the message.  Choose from: black, red, green, 
            yellow, blue, magenta, cyan or white.
        header_color (string)
            Color used to display the header, if one is produced.  Choose from: 
            black, red, green, yellow, blue, magenta, cyan or white.
        """
        self.severity = severity
        self.is_error = is_error
        self.log = log
        self.output = output
        self.terminate = terminate
        self.is_continuation = is_continuation
        self.message_color = Color(message_color)
        self.header_color = Color(header_color)
        self.stream = sys.stderr if self.terminate else sys.stdout

    def __call__(self, *args, **kwargs):
        MESSENGER.report(args, kwargs, self)

    def produce_output(self, messenger):
        # returns a boolean
        return self.write_output(messenger) or self.write_logfile(messenger)

    def write_output(self, messenger):
        # returns a boolean
        try:
            return self.output(messenger)
        except TypeError:
            return self.output

    def write_logfile(self, messenger):
        # returns a boolean
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
codicil = MessengerGenerator(
    is_continuation=True,
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
        logfile=False,
        prog_name=True,
        argv=None,
        version=None,
        termination_callback=None,
        colorscheme='dark',
        flush=False,
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
        logfile (string or stream or bool)
            May be a string, in which case it is taken to be the path of the 
            logfile.  May be *True*, in which case ./.<prog_name>.log is used.  
            May be an open stream.  Or it may be *False*, in which case no log 
            file is created.
        prog_name (string)
            The program name. Is appended to the message headers and used to 
            create the default logfile name. May be a string, in which case it 
            is used as the name of the program.  May be *True*, in which case 
            basename(argv[0]) is used.  May be *False* to indicate that program 
            name should not be added to message headers.
        argv (list of strings)
            Program name By default, basename(argv[0]) is used. Use False to 
            indicate that program name should not be added to message headers.
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
        flush (bool)
            Flush the stream after each write. Is useful if you program is 
            crashing, causing loss of the latest writes. Can cause programs to 
            run considerably slower if they produce a lot of output. Not 
            available with python2.
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
        self.flush = flush
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr
        self.__dict__.update(kwargs)
        self.previous_action = None

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
        if prog_name is True:
            prog_name = os.path.basename(argv[0]) if argv else None
        self.prog_name = prog_name

        # save the logfile (and open if it is a string)
        self.set_logfile(logfile)

        # Save the color scheme
        assert colorscheme in [None, 'light', 'dark']
        self.colorscheme = colorscheme

        # Activate the actions
        global MESSENGER
        MESSENGER = self

        # write header to log file
        if prog_name and version:
            log("%s version %s" % (prog_name, version))
        try:
            import arrow
            now = arrow.now().strftime(
                " on %A, %-d %B %Y at %-I:%M:%S %p")
        except:
            now = ""
        log("Invoked as '%s'%s." % (' '.join(argv), now))

    # __getattr__ {{{2
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        return self.__dict__.get(name)

    # set_logfile {{{2
    def set_logfile(self, logfile):
        try:
            if self.logfile:
                self.logfile.close()
        except:
            pass

        if logfile is True:
            logfile = '.%s.log' % self.prog_name if self.prog_name else '.log'
        if is_str(logfile):
            try:
                logfile = open(logfile, 'w')
            except (IOError, OSError) as err:
                print(os_error(err), file=sys.stderr)
        self.logfile = logfile

    # report {{{2
    def report(self, args, kwargs, action):
        is_continuation = action.is_continuation
        if is_continuation:
            action = self.previous_action
            assert(action)
        else:
            if action.is_error:
                self.errors += 1
        culprit = kwargs.get('culprit')
        if action.produce_output(self):
            options = self._get_print_options(kwargs, action)
            message = self._render_message(args, kwargs)
            header = self._render_header(action, culprit)
            if header:
                if is_continuation:
                    header = ''
                    message = indent(message)
                elif '\n' in message:
                    header = header.rstrip() + '\n'
                    message = indent(message)
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
        self.previous_action = action

    # _get_print_options {{{2
    def _get_print_options(self, kwargs, action):
        opts = {
            'file': kwargs.get(
                'file',
                self.stderr if action.terminate else self.stdout
            ),
            'flush': kwargs.get('flush', self.flush),
        }
        if sys.version[0] == '2':
            # flush is not supported in python2
            opts.pop('flush')
        return opts

    # _render_message {{{2
    @staticmethod
    def _render_message(args, kwargs):
        return kwargs.get('sep', ' ').join(str(arg) for arg in args)

    # _render_header {{{2
    def _render_header(self, action, culprit):
        if action.severity:
            if self.prog_name:
                header = '%s %s: ' % (self.prog_name, action.severity)
            else:
                header = '%s: ' % action.severity

            if culprit:
                if is_collection(culprit):
                    culprit = '.'.join(str(c) for c in culprit)
                header += str(culprit) + ': '
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
        return self.kwargs.get('sep', ' ').join(str(a) for a in self.args)
    def report(self):
        error(*self.args, **self.kwargs)
