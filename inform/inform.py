# Inform
# Utilities for communicating directly with the user.

# License {{{1
# Copyright (C) 2014-2017 Kenneth S. Kundert
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
    r"""
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

    Examples::

        >>> from inform import indent
        >>> print(indent('And the answer is ...\n42!', first=-1))
        And the answer is ...
            42!

    """
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
        elif is_collection(remove):
            return [each for each in collection if each not in remove]
        else:
            return [each for each in collection if each != remove]
    except KeyError:
        return [each for each in collection if each]

# is_str {{{2
def is_str(obj):
    from six import string_types
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
        if '\033' in text:
            return cls.COLOR_CODE_REGEX.sub('', text)
        else:
            return text


# User Utilities {{{1
# fmt {{{2
def fmt(message, *args, **kwargs):
    """
    Convert a message with embedded attributes to a string. The values for the 
    attributes can come from the argument list, as with ''.format(), or they may
    come from the local scope (found by introspection).

    Examples::

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

        | _lvl=0 searches for variables in the scope that calls fmt(), the default
        | _lvl=-1 searches in the parent of the scope that calls fmt()
        | _lvl=-2 searches in the grandparent, etc.
        | _lvl=1 search root scope, etc.
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
def render(obj, sort=None, level=0, tab='    '):
    """
    Recursively convert object to string with reasonable formatting.
    Has built in support for the base Python types (None, bool, int, float, str,
    set, tuple, list, and dict).  If you confine yourself to these types, the
    output of render can be read by the Python interpreter. Other types are
    converted to string with repr().
    """
    from textwrap import dedent

    # define sort function, make it either sort or not based on sort
    if sort is None:
        sort = True if sys.version_info < (3, 6) else False
    if sort:
        def order(keys):
            try:
                return sorted(keys)
            except TypeError:
                # keys is not homogeneous, cannot sort
                return keys
    else:
        def order(keys):
            return keys

    # define function for computing the amount of indentation needed
    def leader(relative_level=0):
        return (level+relative_level)*tab

    code = []
    if type(obj) == dict:
        endcaps = '{ }'
        content = ['%r: %s' % (k, render(obj[k], sort, level+1)) for k in order(obj)]
    elif type(obj) is list:
        endcaps = '[ ]'
        content = [render(v, sort, level+1) for v in obj]
    elif type(obj) is tuple:
        endcaps = '( )'
        content = [render(v, sort, level+1) for v in obj]
    elif type(obj) is set:
        endcaps = '{ }'
        content = [render(v, sort, level+1) for v in order(obj)]
    elif is_str(obj) and '\n' in obj:
        endcaps = None
        content = [
            '"""',
            indent(dedent(obj.strip()), leader(1)),
            leader(0) + '"""'
        ]
    else:
        endcaps = None
        content = [repr(obj)]

    if endcaps:
        endcaps = endcaps.split()
        lcap, rcap = endcaps[0], endcaps[-1]
    else:
        lcap = rcap = ''

    # try joining the content without newlines
    text = lcap + ', '.join(content) + rcap
    if len(text) < 40 and '\n' not in text:
        return text

    # text is too long, spread it over several lines to make it more readable
    if endcaps:
        content = (
            [lcap] + [leader(1) + v + ',' for v in content] + [leader(0) + rcap]
        )
    return '\n'.join(content)

# os_error {{{2
# Generates a reasonable error message for an operating system errors, those 
# generated by OSError and its ilk.
def os_error(err):
    filenames = ' -> '.join(cull([err.filename, getattr(err, 'filename2', None)]))
    text = err.strerror if err.strerror else str(err)
    msg = ': '.join(cull([filenames, text.lower()]))
    return full_stop(msg)

# conjoin {{{2
# Like join, but supports conjunction
def conjoin(iterable, conj=' and ', sep=', '):
    """Conjunction join

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
    '''Pluralize a word

    If count is 1 or has length 1, the singular argument is returned, otherwise
    the plural argument is returned. If plural is None, then it is created by
    adding an 's' to the end of singular argument.
    '''
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


# columns {{{1
def columns(array, pagewidth=79, alignment='<', leader='    '):
    "Distribute array over enough columns to fill the screen."
    textwidth = pagewidth - len(leader)
    width = max([len(e) for e in array])+1
    numcols = max(1, textwidth//(width+1))
    stride = len(array)//numcols + 1
    fmt = '{{:{align}{width}s}}'.format(align=alignment, width=width)
    table = []
    for i in range(len(array)//numcols+1):
        row = []
        for j in range(numcols):
            try:
                row.append(fmt.format(array[stride*j+i]))
            except IndexError:
                pass
        table.append(leader + ' '.join(row).rstrip())
    return '\n'.join(table)


# debug functions {{{2
def _debug(frame_depth, args, kwargs):
    import inspect
    frame = inspect.stack()[frame_depth + 1][0]

    try:
        # If the calling frame is inside a class (deduced based on the presence 
        # of a 'self' variable), name the logger after that class.  Otherwise 
        # if the calling frame is inside a function, name the logger after that 
        # function.  Otherwise name it after the module of the calling scope.
        from pathlib import Path

        self = frame.f_locals.get('self')
        frame_info = inspect.getframeinfo(frame)
        function = frame_info.function
        filename = frame_info.filename
        lineno = frame_info.lineno
        module = frame.f_globals['__name__']

        fname = Path(filename).name

        if self is not None:
            name = '.'.join([
                    self.__class__.__module__,
                    self.__class__.__name__,
                    function,
            ]) + '()'

        elif function != '<module>':
            name = '.'.join([module, function]) + '()'

        else:
            name = module

        highlight_header = Color('magenta', enable=Color.isTTY(sys.stdout))
        highlight_body = Color('blue', enable=Color.isTTY(sys.stdout))

        header = 'DEBUG: {fname}:{lineno}, {name}'.format(
            filename=filename, fname=fname, lineno=lineno, name=name
        )
        body = kwargs.get('sep', ' ').join(str(arg) for arg in args)
        header += ':\n' if body else '.'
        message = highlight_header(header) + highlight_body(indent(body))
        print(message, **kwargs)

    finally:
        # Failing to explicitly delete the frame can lead to long-lived 
        # reference cycles.
        del frame

def ppp(*args, **kwargs):
    '''Print function tailored for debugging.

    Mimics the normal print function, but colors printed output to make it
    easier to see and labels it with the location of the call.
    '''
    frame_depth = 1
    _debug(frame_depth, args, kwargs)

def ddd(*args, **kwargs):
    '''Print arguments function tailored for debugging.

    Pretty-prints its arguments. Arguments may be name or unnamed.
    '''
    # if an argument has __dict__ attribute, render that rather than arg itself
    def expand(arg):
        try:
            return render(arg.__dict__)
        except AttributeError:
            return render(arg)

    args = [
        expand(arg) for arg in args
    ] + [
        '{k} = {v}'.format(k=k, v=expand(v))
        for k, v in sorted(kwargs.items())
    ]
    frame_depth = 1
    _debug(frame_depth, args, kwargs={'sep':'\n'})

def vvv(*args):
    '''Print variables function tailored for debugging.

    Pretty-prints variables from the calling scope. If no arguments are given,
    all variables are printed. If arguments are given, only the variables whose
    value match an argument are printed.
    '''
    from types import ModuleType, FunctionType
    import inspect

    frame_depth = 1
    frame = inspect.stack()[frame_depth][0]
    variables = [(k, frame.f_locals[k]) for k in sorted(frame.f_locals)]
    args = [
        '{k} = {v}'.format(k=k, v=render(v))
        for k, v in variables
        if not k.startswith('_')
        if not isinstance(v, (FunctionType, type, ModuleType))
        if not args or v in args
    ]
    _debug(frame_depth, args, kwargs={'sep':'\n'})

def sss(*args):
    import traceback
    tb = traceback.extract_stack()
    highlight_body = Color('blue', enable=Color.isTTY(sys.stdout))
    stacktrace = []
    for filename, lineno, funcname, text in tb[:-1]:
        filename = 'File {!r}'.format(filename) if filename else None
        lineno = 'line {}'.format(lineno) if lineno else None
        funcname = 'in {}'.format(funcname) if funcname else None
        text = '\n    {}'.format(text) if text else None
        stacktrace.append(', '.join(cull([filename, lineno, funcname, text])))

    import inspect
    frame_depth = 1
    frame = inspect.stack()[frame_depth][0]
    _debug(frame_depth, stacktrace, kwargs={'sep':'\n'})

# InformantFactory class {{{1
# A bit of terminology. The active Inform object is called the informer, 
# whereas the print functions returned from InformantFactory are referred to 
# as informants.
class InformantFactory:
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
log = InformantFactory(
    output=False,
    log=True,
)
comment = InformantFactory(
    output=lambda inform: inform.verbose and not inform.mute,
    log=True,
    message_color='cyan',
)
codicil = InformantFactory(
    is_continuation=True,
)
narrate = InformantFactory(
    output=lambda inform: inform.narrate and not inform.mute,
    log=True,
    message_color='blue',
)
display = InformantFactory(
    output=lambda inform: not inform.quiet and not inform.mute,
    log=True,
)
output = InformantFactory(
    output=lambda inform: not inform.mute,
    log=True,
)
notify = InformantFactory(
    output=False,
    notify=True,
    log=True,
)
debug = InformantFactory(
    severity='DEBUG',
    output=True,
    log=True,
    header_color='magenta',
)
warn = InformantFactory(
    severity='warning',
    header_color='yellow',
    output=lambda inform: not inform.quiet and not inform.mute,
    log=True,
)
error = InformantFactory(
    severity='error',
    is_error=True,
    header_color='red',
    output=lambda inform: not inform.mute,
    log=True,
)
fatal = InformantFactory(
    severity='error',
    is_error=True,
    terminate=1,
    header_color='red',
    output=lambda inform: not inform.mute,
    log=True,
)
panic = InformantFactory(
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
        length_thresh=80,
        culprit_sep = ', ',
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
        length_thresh (integer)
            Split header from body if line length would be greater than
            threshold.
        culprit_sep (string)
            Join string used for culprit collections.
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
        self.__dict__.update(kwargs)
        self.previous_action = None
        self.logfile = None
        self.length_thresh = length_thresh
        self.culprit_sep = culprit_sep

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

    # suppress_output {{{2
    def suppress_output(self, mute):
        self.mute = bool(mute)

    # set_logfile {{{2
    def set_logfile(self, logfile, encoding='utf-8'):
        try:
            if self.logfile:
                self.logfile.close()
        except:
            pass

        if logfile is True:
            logfile = '.%s.log' % self.prog_name if self.prog_name else '.log'
        try:
            if is_str(logfile):
                try:                # python 3
                    logfile = open(logfile, 'w', encoding=encoding)
                except TypeError:   # python 2
                    import codecs
                    logfile = codecs.open(logfile, 'w', encoding=encoding)
            elif logfile:  # pathlib
                try:
                    logfile = logfile.open(mode='w', encoding=encoding)
                except AttributeError:
                    pass
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

        # handle continuations
        is_continuation = action.is_continuation
        if is_continuation:
            action = self.previous_action
            assert(action)
        else:
            if action.is_error:
                self.errors += 1

        # assemble the message
        if action.produce_output(self):
            options = self._get_print_options(kwargs, action)
            message = self._render_message(args, kwargs)
            culprit = self._render_culprit(kwargs)
            header = self._render_header(action)
            multiline = (header or culprit) and (
                '\n' in message or
                len(header + culprit + message) > self.length_thresh
            )
            if is_continuation:
                multiline = bool(header)
                header = ''

            messege_color = action.message_color
            header_color = action.header_color
            if action.write_output(self):
                cs = self.colorscheme if Color.isTTY(options['file']) else None
                self._show_msg(
                    header_color(header, scheme=cs) if header else header,
                    header_color(culprit, scheme=cs) if culprit else culprit,
                    messege_color(message, scheme=cs) if message else message,
                    multiline,
                    options
                )
            if action.write_logfile(self) and self.logfile:
                options['file'] = self.logfile
                self._show_msg(
                    header,
                    culprit,
                    Color.strip_colors(message),
                    multiline,
                    options
                )
            if action.notify_user(self):
                import subprocess
                body = ': '.join(cull([header, culprit, message]))
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
        template = kwargs.get('template')
        if template is None:
            message = kwargs.get('sep', ' ').join(str(arg) for arg in args)
        else:
            message = template.format(*args, **kwargs)
        wrap = kwargs.get('wrap')
        if wrap:
            from textwrap import fill
            if type(wrap) == int:
                message = fill(message, width=wrap)
            else:
                message = fill(message)
        return message

    # _render_culprit {{{2
    def _render_culprit(self, kwargs):
        culprit = kwargs.get('culprit')
        if culprit:
            if is_collection(culprit):
                return self.culprit_sep.join(str(c) for c in culprit if c)
            else:
                return str(culprit)
        else:
            return ''

    # _render_header {{{2
    def _render_header(self, action):
        if action.severity:
            if self.output_prog_name and self.prog_name:
                return '%s %s' % (self.prog_name, action.severity)
            else:
                return '%s' % action.severity
        return ''

    # show_msg {{{2
    def _show_msg(self, header, culprit, message, multiline, options):
        if multiline:
            head = ': '.join(cull([header, culprit]))
            if head:
                print('%s:\n%s' % (head, indent(message)), **options)
            else:
                print(indent(message), **options)
        else:
            print(': '.join(cull([header, culprit, message])), **options)

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
            | None: return 1 if errors occurred and 0 otherwise
            | 0: success
            | 1: unexpected error
            | 2: invalid invocation
            | 3: panic

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

    # get_prog_name {{{2
    def get_prog_name(self, default):
        "Returns the program name"
        return self.prog_name if self.prog_name else default

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

# get_prog_name {{{3
def get_prog_name(default):
    return INFORMER.get_prog_name(default)


# Instantiate default informer {{{1
DEFAULT_INFORMER = Inform()
INFORMER = DEFAULT_INFORMER


# Exceptions {{{1
# Error {{{2
class Error(Exception):
    """A generic exception.

    The exception accepts both unnamed and named arguments.
    All are recorded and available for later use.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_message(self):
        """Get exception message.

        If the *template* keyword argument was specified, it is treated as a
        format string and is passed both the unnamed and named arguments. The
        resulting string is treated as the message and returned.

        Otherwise the unnamed are joined using spaces to form the message.
        """

        template = self.kwargs.get('template')
        if template is None:
            sep = self.kwargs.get('sep', ' ')
            message = sep.join(str(arg) for arg in self.args)
        else:
            message = template.format(*self.args, **self.kwargs)
        return message

    def get_culprit(self):
        """Get exception culprit.

        If the *culprit* keyword argument was specified as a string, it is
        returned. If it was specified as a collection, the members are converted
        to strings and joined with commas. The resulting string is returned.
        """

        culprit = self.kwargs.get('culprit')
        if is_collection(culprit):
            return ', '.join(str(c) for c in culprit if c is not None)
        elif culprit:
            return str(culprit)

    def report(self):
        """Report exception.

        The :func:`inform.error` function is called with the exception arguments.
        """
        error(*self.args, **self.kwargs)

    def terminate(self):
        """Report exception and terminate.

        The :func:`inform.fatal` function is called with the exception arguments.
        """
        fatal(*self.args, **self.kwargs)

    def __str__(self):
        message = self.get_message()
        culprit = self.get_culprit()
        return "%s: %s" % (culprit, message) if culprit else message

    def __getattr__(self, name):
        # returns the value associated with name in kwargs if it exists, 
        # otherwise None
        if name.startswith('__'):
            raise AttributeError(name)
        return self.kwargs.get(name)
