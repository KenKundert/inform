# Inform
# Utilities for communicating directly with the user.

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
INFORMER = None
NOTIFIER = 'notify-send'


# Inform Utilities {{{1
# indent {{{2
def indent(text, leader='    ', first=0, stops=1, sep='\n'):
    r"""{
    Add indentation.

    leader (string):
        the string added to be beginning of a line to indent it.
    first (integer):
        number of indentations for the first line relative to others (may be 
        negative but (first + stops) should not be).
    stops (integer):
        number of indentations (number of leaders to add to beginning lines).
    sep (string):
        the string used to separate the lines

    Examples:
    >>> from inform import indent
    >>> print(indent('And the answer is ...\n42!', first=-1))
    And the answer is ...
        42!

    }"""
    # do the indent
    indented = (first+stops)*leader + (sep+stops*leader).join(text.split('\n'))

    # resplit it and replace the blank lines with empty lines
    return '\n'.join([line.rstrip() for line in indented.split('\n')])

# cull {{{2
def cull(collection, **kwargs):
    """Cull items of a particular value from a list."""
    try:
        remove = kwargs['remove']
        if callable(remove):
            return [each for each in collection if not remove(each)]
        else:
            return [each for each in collection if each != remove]
    except KeyError:
        return [each for each in collection if each]

# is_str {{{2
from six import string_types
def is_str(obj):
    """Identifies strings in all their various guises."""
    return isinstance(obj, string_types)

# is_iterable {{{2
import collections
def is_iterable(obj):
    """Identifies objects that can be iterated over, including strings."""
    return isinstance(obj, collections.Iterable)

# is_collection {{{2
def is_collection(obj):
    """Identifies objects that can be iterated over, excluding strings."""
    return is_iterable(obj) and not is_str(obj)

# Color class {{{2
class Color:
    """Color

    Used to create colorizers, which are used to render text in a particular 
    color.
    """
    COLORS = ['black','red','green','yellow','blue','magenta','cyan','white'] 
        # The order of the above colors must match order of the standard 
        # terminal
    COLOR_CODE_REGEX = re.compile('\033' + r'\[[01](;\d\d)?m')

    def __init__(self, color, scheme=True, enable=True):
        self.color = color
        self.scheme = 'dark' if scheme is True else scheme
        self.enable = enable

    def __call__(self, *args, **kwargs):
        # scheme is acting as an override, and False prevents the override.
        text = kwargs.get('sep', ' ').join(str(a) for a in args)
        scheme = kwargs.get('scheme', self.scheme)
        if scheme and self.color and self.enable:
            assert self.color in self.COLORS
            bright = 1 if scheme == 'light' else 0
            prefix = '\033[%s;3%dm' % (bright, self.COLORS.index(self.color))
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
    def strip_colors(cls, text):
        return cls.COLOR_CODE_REGEX.sub('', text)


# User Utilities {{{1
# fmt {{{2
def fmt(message, *args, **kwargs):
    r"""
    Convert a message with embedded attributes to a string. The values for the 
    attributes can come from the argument list, as with ''.format(), or they may
    come from the local scope (found by introspection).

    Examples:
    >>> from inform import fmt
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

    You can change the level at which the introspection occurs using the _lvl 
    keyword argument.
       _lvl=0 searches for variables in the scope that calls fmt(), the default
       _lvl=-1 searches in the parent of the scope that calls fmt()
       _lvl=-2 searches in the grandparent, etc.
       _lvl=1 search root scope, etc.
    """
    import inspect

    # Inspect variables from the source frame.
    level = kwargs.pop('_lvl', 0)
    level = 1 - level if level <= 0 else -level
    frame = inspect.stack()[level][0]

    # Collect all the variables in the scope of the calling code, so they 
    # can be substituted into the message.
    attrs = {}
    attrs.update(frame.f_globals)
    attrs.update(frame.f_locals)
    attrs.update(kwargs)

    return message.format(*args, **attrs)

# render {{{2
def render(obj, _level=0):
    """
    Recursively convert object to string with reasonable formatting.
    Has built in support for the base Python types (None, bool, int, float, str,
    set, tuple, list, and dict).  If you confine yourself to these types, the
    output of render can be read by the Python interpreter. Other types are
    converted to string with repr().
    """

    from textwrap import dedent

    def leader(relative_level=0):
        return (_level+relative_level)*'    '
    code = []
    if type(obj) == dict:
        code += ['{']
        try:
            keys = sorted(obj.keys())
        except TypeError: # keys have heterogeneous types, cannot be sorted
            keys = obj.keys()
        for key in keys:
            value = obj[key]
            code += ['%s%r: %s,' % (
                leader(1), key, render(value, _level+1)
            )]
        code += ['%s}' % (leader(0))]
    elif type(obj) == list:
        code += ['[']
        for each in obj:
            code += ['%s%s,' % (
                leader(1), render(each, _level+1)
            )]
        code += ['%s]' % (leader(0))]
    elif type(obj) == tuple:
        code += ['(']
        for each in obj:
            code += ['%s%s,' % (
                leader(1), render(each, _level+1)
            )]
        code += ['%s)' % (leader(0))]
    elif type(obj) == set:
        code += ['{']
        try:
            members = sorted(obj)
        except TypeError: # members have heterogeneous types, cannot be sorted
            members = obj
        for each in members:
            code += ['%s%s,' % (
                leader(1), render(each, _level+1)
            )]
        code += ['%s}' % (leader(0))]
    elif is_str(obj) and '\n' in obj:
        code += ['"""' + indent(dedent(obj), leader(1)) + leader(0) + '"""']
    else:
        code += [repr(obj)]
    return '\n'.join(code)

# os_error {{{2
# Generates a reasonable error message for an operating system errors, those 
# generated by OSError and its ilk.
def os_error(err):
    filenames = ' -> '.join(cull([err.filename, getattr(err, 'filename2', None)]))
    msg = ': '.join(cull([filenames, err.strerror.lower()]))
    return full_stop(msg)

# conjoin {{{2
# Like join, but supports conjunction
def conjoin(iterable, conj=' and ', sep=', '):
    """
    Conjunction Join
    Return the list joined into a string, where conj is used to join the last
    two items in the list, and sep is used to join the others.

    Examples:
    >>> from inform import conjoin
    >>> print(conjoin([], ' or '))
    <BLANKLINE>

    >>> print(conjoin(['a'], ' or '))
    a

    >>> print(conjoin(['a', 'b'], ' or '))
    a or b

    >>> print(conjoin(['a', 'b', 'c']))
    a, b and c

    """
    lst = list(iterable)
    if conj is not None and len(lst) > 1:
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


# full_stop {{{2
def full_stop(sentence):
    """Add period to end of string if it is needed

    full_stop(str) --> str
    A period (full stop) is added if there is no terminating punctuation at the
    end of the string.
    """
    sentence = str(sentence)
    return sentence if sentence[-1] in '.?!' else sentence + '.'


# InformantGenerator class {{{1
# A bit of terminology. The active Inform object is called the informer, 
# whereas the print functions returned from InformantGenerator are referred to 
# as informants.
class InformantGenerator:
    def __init__(
        self,
        severity=None,
        is_error=False,
        log=True,
        output=True,
        notify=False,
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
            accepts the informer as an argument and returns a boolean.
        output (bool)
            Send message to the output stream.  May be a boolean or a function 
            that accepts the informer as an argument and returns a boolean.
        notify (bool)
            Send message to the notifier.  The notifier will display the message
            that appears temporarily in a bubble at the top of the screen.
            May be a boolean or a function that accepts the informer as an
            argument and returns a boolean.
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
        self.notify = notify
        self.terminate = terminate
        self.is_continuation = is_continuation
        self.message_color = Color(message_color)
        self.header_color = Color(header_color)
        self.stream = sys.stderr if self.terminate else sys.stdout

    def __call__(self, *args, **kwargs):
        INFORMER.report(args, kwargs, self)

    def produce_output(self, informer):
        "Will informant produce output either directly to the user or to the logfile?"
        return (
            self.write_output(informer) or self.write_logfile(informer) or
            self.notify_user(informer)
        )

    def write_output(self, informer):
        "Will informant produce output directly to the user?"
        try:
            return self.output(informer)
        except TypeError:
            return self.output

    def write_logfile(self, informer):
        "Will informant produce output to the logfile?"
        # returns a boolean
        try:
            return self.log(informer)
        except TypeError:
            return self.log

    def notify_user(self, informer):
        "Will informant produce output to the notifier?"
        # returns a boolean
        try:
            return self.notify(informer)
        except TypeError:
            return self.notify


# Informants {{{1
log = InformantGenerator(
    output=False,
    log=True,
)
comment = InformantGenerator(
    output=lambda inform: inform.verbose and not inform.mute,
    log=True,
    message_color='cyan',
)
codicil = InformantGenerator(
    is_continuation=True,
)
narrate = InformantGenerator(
    output=lambda inform: inform.narrate and not inform.mute,
    log=True,
    message_color='blue',
)
display = InformantGenerator(
    output=lambda inform: not inform.quiet and not inform.mute,
    log=True,
)
output = InformantGenerator(
    output=lambda inform: not inform.mute,
    log=True,
)
notify = InformantGenerator(
    output=lambda inform: not inform.quiet and not inform.mute,
    notify=True,
    log=True,
)
debug = InformantGenerator(
    severity='DEBUG',
    output=True,
    log=True,
    header_color='magenta',
)
warn = InformantGenerator(
    severity='warning',
    header_color='yellow',
    output=lambda inform: not inform.quiet and not inform.mute,
    log=True,
)
error = InformantGenerator(
    severity='error',
    is_error=True,
    header_color='red',
    output=lambda inform: not inform.mute,
    log=True,
)
fatal = InformantGenerator(
    severity='error',
    is_error=True,
    terminate=1,
    header_color='red',
    output=lambda inform: not inform.mute,
    log=True,
)
panic = InformantGenerator(
    severity='internal error (please report)',
    is_error=True,
    terminate=3,
    header_color='red',
    output=True,
    log=True,
)


# Inform class {{{1
class Inform:
    """Inform

    Handles all informants, which in turn handle user messaging.  Generally 
    copies messages to the logfile while sending most to standard out as well, 
    however all is controllable.
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
        hanging_indent=True,
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
            ignored by Inform, but may be accessed by the informants.
        """
        self.errors = 0
        self.version = version
        self.termination_callback = termination_callback
        self.flush = flush
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr
        self.hanging_indent = bool(hanging_indent)
        self.__dict__.update(kwargs)
        self.previous_action = None
        self.logfile = None

        # make verbosity flags consistent
        self.mute = mute
        self.quiet = quiet
        if quiet:
            self.verbose = self.narrate = False
        else:
            self.verbose = verbose
            self.narrate = narrate

        # determine program name
        if argv is None:
            argv = sys.argv
        self.output_prog_name = bool(prog_name)
        if not is_str(prog_name):
            if argv[0]:
                prog_name = os.path.basename(argv[0])
            else:
                prog_name = os.path.basename(sys.argv[0])
        self.prog_name = prog_name
        self.argv = argv

        # Save the color scheme
        assert colorscheme in [None, 'light', 'dark']
        self.colorscheme = colorscheme

        # Activate the actions
        global INFORMER
        INFORMER = self

        # activate the logfile
        self.set_logfile(logfile)

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
                logfile = None
        self.logfile = logfile
        if not logfile:
            return

        # write header to log file
        if self.prog_name and self.version:
            log("%s - version %s" % (self.prog_name, self.version))
        try:
            import arrow
            now = arrow.now().strftime(" on %A, %-d %B %Y at %-I:%M:%S %p")
        except:
            now = ""
        if self.argv:
            log("Invoked as '%s'%s." % (' '.join(self.argv), now))
        elif now:
            log("Invoked%s." % now)

    # flush_logfile {{{2
    def flush_logfile(self):
        if self.logfile:
            self.logfile.flush()

    # report {{{2
    def report(self, args, kwargs, action):
        is_continuation = action.is_continuation
        if is_continuation:
            action = self.previous_action
            assert(action)
        else:
            if action.is_error:
                self.errors += 1
        if action.produce_output(self):
            options = self._get_print_options(kwargs, action)
            message = self._render_message(args, kwargs)
            culprit = self._render_culprit(kwargs)
            header = self._render_header(action)
            body = message
            hang = 1*bool(kwargs.get('hanging', self.hanging_indent))
            if culprit:
                culprit = str(culprit)
                if len(culprit) + len(header) > 40:
                    body = '%s:\n%s' % (
                        culprit,
                        indent(body, first=-hang, stops=1 + (not header)*hang)
                    )
                else:
                    body = '%s: %s' % (culprit, body)
            if header:
                if is_continuation:
                    header = ''
                    body = indent(body, first=-hang, stops=1+hang)
                elif '\n' in body:
                    body = '\n' + indent(body, first=-hang, stops=1+hang)
                    header = header.rstrip()
            messege_color = action.message_color
            header_color = action.header_color
            if action.write_output(self):
                cs = self.colorscheme if Color.isTTY(options['file']) else None
                if header:
                    print(
                        header_color(header, scheme=cs)
                      + messege_color(body, scheme=cs),
                        **options
                    )
                else:
                    print(messege_color(body, scheme=cs), **options)
            if action.write_logfile(self) and self.logfile:
                options['file'] = self.logfile
                print('%s%s' % (header, body), **options)
            if action.notify_user(self):
                import subprocess
                subprocess.call(cull([NOTIFIER, self.prog_name, body]))
        if action.terminate is not False:
            self.terminate(status=action.terminate)
        self.previous_action = action

    # _get_print_options {{{2
    def _get_print_options(self, kwargs, action):
        opts = {
            # 'sep': kwargs.get('sep', ' '), -- handled in _render_message
            'end': kwargs.get('end', '\n'),
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

    # _render_culprit {{{2
    @staticmethod
    def _render_culprit(kwargs):
        culprit = kwargs.get('culprit')
        if culprit and is_collection(culprit):
            culprit = ', '.join(str(c) for c in culprit if c is not None)
        return culprit

    # _render_header {{{2
    def _render_header(self, action):
        if action.severity:
            if self.output_prog_name and self.prog_name:
                return '%s %s: ' % (self.prog_name, action.severity)
            else:
                return '%s: ' % action.severity
        return ''

    # done {{{2
    def done(self):
        "Normal termination"
        if self.termination_callback:
            self.termination_callback()
        if self.prog_name:
            log('%s: terminates normally.' % self.prog_name)
        else:
            log('program terminates normally.')
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        sys.exit()

    # terminate {{{2
    def terminate(self, status=None):
        """Termination

        Recommended status codes:
            None: return 1 if errors occurred and 0 otherwise
            0: success
            1: unexpected error
            2: invalid invocation
            3: panic
        Status may also be a string, in which case it is printed to stderr and 
        the exit status is 1.
        """
        if status is None or status is True:
            status = 1 if self.errors_accrued() else 0
        prog_name = self.prog_name if self.prog_name else sys.argv[0]
        if self.termination_callback:
            self.termination_callback()
        if is_str(status):
            log("%s: terminates with status '%s'." % (prog_name, status))
        else:
            log('%s: terminates with status %s.' % (prog_name, status))
            assert 0 <= status and status < 128
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        sys.exit(status)

    # terminate_if_errors {{{2
    def terminate_if_errors(self, status=1):
        "Terminate if error count is nonzero"
        if self.errors:
            self.terminate(status)

    # errors_accrued {{{2
    def errors_accrued(self, reset=False):
        "Returns number of errors that have accrued"
        count = self.errors
        if reset:
            self.errors = 0
        return count

    # disconnect {{{2
    def disconnect(self):
        "Disconnect informer"
        if self.logfile:
            self.logfile.flush()
        global INFORMER
        INFORMER = DEFAULT_INFORMER

    # __enter__ {{{2
    def __enter__(self):
        return self

    # __exit__ {{{2
    def __exit__(self, type, value, traceback):
        self.disconnect()

# Direct access to class methods {{{2
# done {{{3
def done():
    INFORMER.done()

# terminate {{{3
def terminate(status=True):
    INFORMER.terminate(status)

# terminate_if_errors {{{3
def terminate_if_errors(status=1):
    INFORMER.terminate_if_errors(status)

# errors_accrued {{{3
def errors_accrued(reset=False):
    return INFORMER.errors_accrued(reset)


# Instantiate default informer {{{1
DEFAULT_INFORMER = Inform()
INFORMER = DEFAULT_INFORMER


# Exceptions {{{1
# Error {{{2
class Error(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_message(self):
        return self.kwargs.get('sep', ' ').join(str(a) for a in self.args)

    def get_culprit(self):
        culprit = self.kwargs.get('culprit')
        if is_collection(culprit):
            return ', '.join(str(c) for c in culprit if c is not None)
        elif culprit:
            return str(culprit)

    def __str__(self):
        message = self.get_message()
        culprit = self.get_culprit()
        return "%s: %s" % (culprit, message) if culprit else message

    def report(self):
        error(*self.args, **self.kwargs)

    def terminate(self):
        fatal(*self.args, **self.kwargs)

    # __getattr__ {{{2
    def __getattr__(self, name):
        # returns the value associated with name in kwargs if it exists, 
        # otherwise None
        if name.startswith('__'):
            raise AttributeError(name)
        return self.kwargs.get(name)
