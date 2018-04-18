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
import re
import os
import sys

# Globals {{{1
INFORMER = None
NOTIFIER = 'notify-send'
STREAM_POLICIES = {
    'termination': lambda i, so, se: se if i.terminate else so,
        # stderr is used on final termination message
    'header':  lambda i, so, se: se if i.severity else so,
        # stderr is used on all messages that include headers
}


# Inform Utilities {{{1
# indent {{{2
def indent(text, leader='    ', first=0, stops=1, sep='\n'):
    r"""
    Add indentation.

    Args:
        leader (string):
            the string added to be beginning of a line to indent it.

        first (integer):
            number of indentations for the first line relative to others (may be
            negative but (first + stops) should not be).

        stops (integer):
            number of indentations (number of leaders to add to beginning lines).

        sep (string):
            the string used to separate the lines

    Example::

        >>> from inform import display, indent
        >>> display(indent('And the answer is ...\n42!', first=-1))
        And the answer is ...
            42!

    """
    # do the indent
    indented = (first+stops)*leader + (sep+stops*leader).join(text.split('\n'))

    # resplit it and replace the blank lines with empty lines
    return '\n'.join([line.rstrip() for line in indented.split('\n')])


# cull {{{2
def cull(collection, **kwargs):
    """Cull items of a particular value from a collection.

    Args:
        collection:
            The collection may be list-like (list, tuples, sets, etc.) or
            dictionary-like (dict, OrderedDict, etc.).  A new collection of the
            same type is returned with the undesirable values removed.

        remove:
            Must be specified as keyword argument. May be a function, a
            collection, or a scalar.  The function would take a single argument,
            one of the values in the collection, and return True if the value
            should be culled. The scalar or the collection simply specified the
            specific value or values to be culled.

            If remove is not specified, the value is culled if its value would
            be False when cast to a boolean (0, False, None, '', (), [], {}, etc.)

    Example::

        >>> from inform import cull, display
        >>> from collections import OrderedDict
        >>> fruits = OrderedDict([
        ...    ('a','apple'), ('b','banana'), ('c','cranberry'), ('d','date'),
        ...    ('e',None), ('f',None), ('g','guava'),
        ... ])
        >>> display(*cull(list(fruits.values())), sep=', ')
        apple, banana, cranberry, date, guava

        >>> for k, v in cull(fruits).items():
        ...     display('{k} is for {v}'.format(k=k, v=v))
        a is for apple
        b is for banana
        c is for cranberry
        d is for date
        g is for guava

    """
    # convert remove into a function
    if 'remove' in kwargs:
        if callable(kwargs['remove']):
            remove = kwargs['remove']
        elif is_collection(kwargs['remove']):
            remove = lambda x: x in kwargs['remove']
        else:
            remove = lambda x: x == kwargs['remove']
    else:
        remove = lambda x: not x

    # cull the herd
    try:
        items = [(k,v) for k, v in collection.items() if not remove(v)]
        return collection.__class__(items)
    except (AttributeError, TypeError):
        values = [v for v in collection if not remove(v)]
        return collection.__class__(values)


# is_str {{{2
def is_str(arg):
    """Identifies strings in all their various guises.

    Returns *True* if argument is a string.

    Example::

        >>> from inform import is_str
        >>> is_str('abc')
        True

        >>> is_str(['a', 'b', 'c'])
        False

    """
    from six import string_types

    return isinstance(arg, string_types)


# is_iterable {{{2
def is_iterable(obj):
    """Identifies objects that can be iterated over, including strings.

    Returns *True* if argument is a collecton or a string.

    Example::

        >>> from inform import is_iterable
        >>> is_iterable('abc')
        True

        >>> is_iterable(['a', 'b', 'c'])
        True

    """
    import collections
    return isinstance(obj, collections.Iterable)


# is_collection {{{2
def is_collection(obj):
    """Identifies objects that can be iterated over, excluding strings.

    Returns *True* if argument is a collecton (tuple, list, set or dictionary).

    Example::

        >>> from inform import is_collection
        >>> is_collection('abc')
        False

        >>> is_collection(['a', 'b', 'c'])
        True

    """
    return is_iterable(obj) and not is_str(obj)

# Color class {{{2
class Color:
    """Color

    Used to create colorizers, which are used to render text in a particular
    color.

    Args:
        color (string):
            The desired color. Choose from:
            *black* *red* *green* *yellow* *blue* *magenta* *cyan* *white*.
        scheme (string):
            Use the specified colorscheme when rendering the text.
            Choose from *None*, 'light' or 'dark', default is 'dark'.
        enalbe (bool):
            If set to False, the colorizer does not render the text in color.

    Example:

        >>> from inform import Color
        >>> fail = Color('red')

    In this example, *fail* is a colorizer. It behave just like
    :func:`inform.join` in that it combines its arguments into a string that
    it returns. The difference is that colorizers add color codes that will
    cause most terminals to display the string in the desired color.

    Like :func:`inform.join`, colorizers take the following arguments:

        unnamed arguments:
            The unnamed arguments are converted to strings and joined to form
            the text to be colored.

        sep = ' ':
            The join string, used when joining the unnamed arguments.

        template = None:
            A template that if present interpolates the arguments to form the
            final message rather than simply joining the unnamed arguments with
            *sep*. The template is a string, and its *format* method is called
            with the unnamed and named arguments of the message passed as
            arguments.

        wrap = False:
            Specifies whether message should be wrapped. *wrap* may be True, in
            which case the default width of 70 is used.  Alternately, you may
            specify the desired width. The wrapping occurs on the final message
            after the arguments have been joined.

        scheme = *False*:
            Use to override the colorscheme when rendering the text.  Choose
            from *None*, *False*, 'light' or 'dark'.  If you specify *False*
            (the default), the colorscheme specified when creating the colorizer
            is used.
    """
    COLORS = 'black red green yellow blue magenta cyan white'.split()
        # The order of the above colors must match order
        # of the standard terminal
    COLOR_CODE_REGEX = re.compile('\033' + r'\[[01](;\d\d)?m')

    def __init__(self, color, scheme=True, enable=True):
        self.color = color
        self.scheme = 'dark' if scheme is True else scheme
        self.enable = enable

    def __call__(self, *args, **kwargs):
        text = _join(args, kwargs)

        # scheme is acting as an override, and False prevents the override.
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
        """Takes a stream as an argument and returns true if it is a TTY.

        If not given, *stdout* is used as the stream.

        >>> from inform import Color, display
        >>> import sys, re

        >>> if Color.isTTY(sys.stdout):
        ...     emphasize = Color('magenta')
        ... else:
        ...     emphasize = str.upper

        >>> def highlight(matchobj):
        ...     return emphasize(matchobj.group(0))

        >>> display(re.sub('your', highlight, 'Imagine your city without cars.'))
        Imagine YOUR city without cars.

        """
        try:
            return os.isatty(stream.fileno())
        except Exception:
            return False

    @classmethod
    def strip_colors(cls, text):
        """Takes a string as its input and return that string stripped of any color codes."""
        if '\033' in text:
            return cls.COLOR_CODE_REGEX.sub('', text)
        else:
            return text


# User Utilities {{{1
# join {{{2
def join(*args, **kwargs):
    """Combines arguments into a string.

    Combines the arguments in a manner very similar to an informant and returns
    the result as a string.  Uses the *sep*, *template* and *wrap* keyword
    arguments to combine the arguments.

    If *template* is specified it controls how the arguments are combined and
    the result returned.  Otherwise the unnamed arguments are joined using the
    separator and returned.

    Args:
        sep (string):
            Use specified string as join string rather than single space.
            The unnamed arguments will be joined with using this string as a
            separator. Default is ' '.

        template (string or collection of strings):
            A python format string. If specified, the unnamed and named arguments
            are combined under the control of the strings format method. This
            may also be a collection of strings, in which case each is tried in
            sequence, and the first for which all the interpolated arguments are
            known is used.  By default, an argument is 'known' if it would be
            True if casted to a boolean.

        remove:
            Used if *template* is a collection.

            May be a function, a collection, or a scalar.  The function would
            take a single argument, one of the values in the collection, and
            return True if the value should not be considered known. The scalar
            or the collection simply specified the specific value of values that
            should not be considered known.

            If remove is not specified, the value should not be considered known
            if its value would be False when cast to a boolean (0, False, None,
            '', (), [], {}, etc.)

        wrap = False:
            If true the string is wrapped using a width of 70. If an integer value
            is passed, is used as the width of the wrap.

    Examples::

        >>> from inform import join
        >>> join('a', 'b', 'c', x='x', y='y', z='z')
        'a b c'

        >>> join('a', 'b', 'c', x='x', y='y', z='z', template='{2} {z}')
        'c z'

    """
    return _join(args, kwargs)


# _join {{{2
def _join(args, kwargs):
    template = kwargs.get('template')
    if template is None:
        message = kwargs.get('sep', ' ').join(str(arg) for arg in args)
    else:
        if is_str(template):
            message = template.format(*args, **kwargs)
        else:
            remove = dict(remove=kwargs['remove']) if 'remove' in kwargs else {}
            kwargs_filtered = cull(kwargs, **remove)
            args_filtered = cull(args, **remove)

            for tmplt in template:
                try:
                    message = tmplt.format(*args_filtered, **kwargs_filtered)
                    break
                except (KeyError, IndexError):
                    pass
            else:
               raise KeyError('no template match.')

    wrap = kwargs.get('wrap')
    if wrap:
        from textwrap import fill
        if type(wrap) == int:
            message = fill(message, width=wrap)
        else:
            message = fill(message)
    return message


# render {{{2
def render(obj, sort=None, level=0, tab='    '):
    """
    Recursively convert object to string with reasonable formatting.  Has built
    in support for the base Python types (*None*, *bool*, *int*, *float*, *str*,
    *set*, *tuple*, *list*, and *dict*).  If you confine yourself to these
    types, the output of render can be read by the Python interpreter.  Other
    types are converted to string with *repr()*.

    The dictionary keys and set values are sorted if sort is *True*. Sometimes
    this is not possible because the values are not comparable, in which case
    render reverts to the natural order.

    Example::

        >>> from inform import display, render
        >>> display('result =', render({'a': (0, 1), 'b': [2, 3, 4]}))
        result = {'a': (0, 1), 'b': [2, 3, 4]}

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

    if type(obj) == dict:
        endcaps = '{ }'
        content = [
            '%r: %s' % (k, render(obj[k], sort, level+1))
            for k in order(obj)
        ]
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


# fmt {{{2
def fmt(message, *args, **kwargs):
    """
    Similar to ''.format(), but it can pull arguments from the local scope.

    Convert a message with embedded attributes to a string. The values for the
    attributes can come from the argument list, as with ''.format(), or they
    may come from the local scope (found by introspection).

    Examples::

        >>> from inform import fmt
        >>> s = 'str var'
        >>> d = {'msg': 'dict val'}
        >>> class Class:
        ...     a = 'cls attr'

        >>> display(fmt("by order: {0}, {1[msg]}, {2.a}.", s, d, Class))
        by order: str var, dict val, cls attr.

        >>> display(fmt("by name: {S}, {D[msg]}, {C.a}.", S=s, D=d, C=Class))
        by name: str var, dict val, cls attr.

        >> display(fmt("by magic: {s}, {d[msg]}, {c.a}."))
        by magic: str var, dict val, cls attr.

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


# os_error {{{2
# Generates a reasonable error message for an operating system errors, those
# generated by OSError and its ilk.
def os_error(err):
    """Generates clean messages for operating system errors.

    Example::

        >>> from inform import display, os_error
        >>> try:
        ...     with open('config') as f:
        ...         contents = f.read()
        ... except (OSError, IOError) as e:
        ...     display(os_error(e))
        config: no such file or directory.

    """

    filenames = ' -> '.join(
        cull([err.filename, getattr(err, 'filename2', None)])
    )
    text = err.strerror if err.strerror else str(err)
    msg = ': '.join(cull([filenames, text.lower()]))
    return full_stop(msg)


# conjoin {{{2
# Like string join method, but supports conjunction
def conjoin(iterable, conj=' and ', sep=', '):
    """Conjunction join

    Return the items of the *iterable* joined into a string, where *conj* is
    used to join the last two items in the list, and *sep* is used to join the
    others.

    Examples:

        >>> from inform import conjoin, display
        >>> display(conjoin([], ' or '))
        <BLANKLINE>

        >>> display(conjoin(['a'], ' or '))
        a

        >>> display(conjoin(['a', 'b'], ' or '))
        a or b

        >>> display(conjoin(['a', 'b', 'c']))
        a, b and c

    """
    lst = list(iterable)
    if conj is not None and len(lst) > 1:
        lst = lst[0:-2] + [lst[-2] + conj + lst[-1]]
    return sep.join(lst)


# plural {{{2
def plural(count, singular, plural=None):
    '''Pluralize a word

    If *count* is 1 or has length 1, the *singular* argument is returned,
    otherwise the *plural* argument is returned. If *plural* is None, then it is
    created by adding an 's' to the end of *singular* argument.

    Example::

        >>> from inform import display, plural
        >>> fruits = 'apple banana cranberry date'.split()
        >>> display('I have {} {} of fruit.'.format(len(fruits), plural(fruits, 'piece')))
        I have 4 pieces of fruit.

    '''
    if plural is None:
        plural = singular + 's'
    if is_iterable(count):
        return singular if len(count) == 1 else plural
    else:
        return singular if count == 1 else plural


# full_stop {{{2
def full_stop(sentence):
    """Add period to end of string if it is needed.

    A full stop (a period) is added if there is no terminating punctuation at the
    end of the string.

    Examples::

        >>> from inform import full_stop
        >>> full_stop('The file is out of date')
        'The file is out of date.'

        >>> full_stop('The file is out of date.')
        'The file is out of date.'

        >>> full_stop('Is the file is out of date?')
        'Is the file is out of date?'

    """
    sentence = str(sentence)
    return sentence if sentence[-1] in '.?!' else sentence + '.'


# columns {{{2
def columns(array, pagewidth=79, alignment='<', leader='    '):
    """Distribute array over enough columns to fill the screen.

    Returns a list of strings, one for each line.

    Args:
        array (collection of strings):
            The array to be printed.

        pagewidth (int):
            The number of characters available for each line.

        alignment ('<' or '>'):
            Whether to left ('<') or right ('>') align the *array* items in
            their columns.

        leader (str):
            The string to prepend to each line.

    Example::

        >>> from inform import columns, display, full_stop
        >>> title = 'Display the NATO phonetic alphabet'
        >>> words = '''
        ...     Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett
        ...     Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango
        ...     Uniform Victor Whiskey X-ray Yankee Zulu
        ... '''.split()
        >>> newline = '''
        ... '''
        >>> display(full_stop(title), columns(words), sep=newline)
        Display the NATO phonetic alphabet.
            Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
            Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
            Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
            Delta     Hotel     Lima      Papa      Tango     X-ray

    """
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
        body = _join(args, kwargs)
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

    Pretty-prints its arguments. Arguments may be named or unnamed.
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
    _debug(frame_depth, args, kwargs=dict(sep='\n'))


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
    _debug(frame_depth, args, kwargs=dict(sep='\n'))


def sss():
    "Print a stack trace."
    import traceback
    tb = traceback.extract_stack()
    stacktrace = []
    for filename, lineno, funcname, text in tb[:-1]:
        filename = 'File {!r}'.format(filename) if filename else None
        lineno = 'line {}'.format(lineno) if lineno else None
        funcname = 'in {}'.format(funcname) if funcname else None
        text = '\n    {}'.format(text) if text else None
        stacktrace.append(', '.join(cull([filename, lineno, funcname, text])))

    frame_depth = 1
    _debug(frame_depth, stacktrace, kwargs=dict(sep='\n'))


# InformantFactory class {{{1
# A bit of terminology. The active Inform object is called the informer,
# whereas the print functions returned from InformantFactory are referred to
# as informants.
class InformantFactory:
    """
    An object of InformantFactory is referred to as an informant. It is
    generally treated as a function that is called to produce the desired
    output.

    Args:
        severity (string):
            Messages with severities get headers. The header consists of the
            severity, the program name (if desired), and the culprit (if
            provided). If the message text does not contain a newline it is
            appended to the header.  Otherwise the message text is indented and
            placed on the next line.

        is_error (bool):
            Message is counted as an error.

        log (bool):
            Send message to the log file.  May be a boolean or a function that
            accepts the informer as an argument and returns a boolean.

        output (bool):
            Send message to the output stream.  May be a boolean or a function
            that accepts the informer as an argument and returns a boolean.

        notify (bool):
            Send message to the notifier.  The notifier will display the
            message that appears temporarily in a bubble at the top of the
            screen.  May be a boolean or a function that accepts the informer
            as an argument and returns a boolean.

        terminate (bool or integer):
            Terminate the program.  Exit status is the value of *terminate*
            unless *terminate* is *True*, in which case 1 is returned if an
            error occurred and 0 otherwise.

        is_continuation (bool):
            This message is a continuation of the previous message.  It will
            use the properties of the previous message (output, log, message
            color, etc) and if the previous message had a header, that header
            is not output and instead the message is indented.

        message_color (string):
            Color used to display the message.  Choose from: *black*, *red*,
            *green*, *yellow*, *blue*, *magenta*, *cyan* or *white*.

        header_color (string):
            Color used to display the header, if one is produced.  Choose from:
            *black*, *red*, *green*, *yellow*, *blue*, *magenta*, *cyan* or
            *white*.

        stream (stream):
            Output stream to use. Typically sys.stdout or sys.stderr. If not
            specified, the stream to use will be determine by stream policy of
            active informer.

    Example:

        The following generates two informants, *pass*, which prints its
        messages in green, and *fail*, which prints its messages in red.  Output
        to the standard output for both is suppressed if *quiet* is *True*::

            >>> from inform import InformantFactory, Inform

            >>> passes = InformantFactory(
            ...     output=lambda inform: not inform.quiet,
            ...     log=True,
            ...     message_color='green',
            ... )
            >>> fails = InformantFactory(
            ...     output=lambda inform: not inform.quiet,
            ...     log=True,
            ...     message_color='red',
            ... )

        *pass*  and *fail* are both informants. Once created, the can be used to
        give messages to the user::

            >>> results = [
            ...     (0,   0.005, 0.025),
            ...     (0.5, 0.512, 0.025),
            ...     (1,   0.875, 0.025),
            ... ]
            >>> for expected, measured, tolerance in results:
            ...     if abs(expected - measured) > tolerance:
            ...         report, label = fails, 'FAIL'
            ...     else:
            ...         report, label = passes, 'Pass'
            ...     report(
            ...         label, measured, expected, measured-expected,
            ...         template='{}: measured = {:.3f}V, expected = {:.3f}V, diff = {:.3f}V'
            ...     )
            Pass: measured = 0.005V, expected = 0.000V, diff = 0.005V
            Pass: measured = 0.512V, expected = 0.500V, diff = 0.012V
            FAIL: measured = 0.875V, expected = 1.000V, diff = -0.125V

        The passes are rendered in green and the failures in red.
    """

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
        stream=None,
    ):
        self.severity = severity
        self.is_error = is_error
        self.log = log
        self.output = output
        self.notify = notify
        self.terminate = terminate
        self.is_continuation = is_continuation
        self.message_color = Color(message_color)
        self.header_color = Color(header_color)
        self.stream = stream

    def __call__(self, *args, **kwargs):
        INFORMER._report(args, kwargs, self)

    def _produce_output(self, informer):
        "Will informant produce output either directly to user or to logfile?"
        return (
            self._write_output(informer) or self._write_logfile(informer) or
            self._notify_user(informer)
        )

    def _write_output(self, informer):
        "Will informant produce output directly to the user?"
        try:
            return self.output(informer)
        except TypeError:
            return self.output

    def _write_logfile(self, informer):
        "Will informant produce output to the logfile?"
        # returns a boolean
        try:
            return self.log(informer)
        except TypeError:
            return self.log

    def _notify_user(self, informer):
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

    Manages all informants, which in turn handle user messaging.  Generally
    informant copy messages to the logfile while most also send to the standard
    output as well, however all is controllable.

    Args:
        mute (bool):
            All output is suppressed (it is still logged).

            With the provided informants all output is suppressed when set (it
            is still logged). This is generally used when the program being run
            is being run by another program that is generating its own messages
            and does not want the user confused by additional messages. In this
            case, the calling program is responsible for observing and reacting
            to the exit status of the called program.

        quiet (bool):
            Normal output is suppressed (it is still logged).

            With the provided informants normal output is suppressed when set
            (it is still logged). This is used when the user has indicated that
            they are uninterested in any conversational messages and just want
            to see the essentials (generally error messages).

        verbose (bool):
            Comments are output to user, normally they are just logged.

            With the provided informants comments are output to user when set;
            normally they are just logged. Comments are generally used to
            document unusual occurrences that might warrant the user's
            attention.

        narrate (bool):
            Narration is output to user, normally it is just logged.

            With the provided informants narration is output to user when set,
            normally it is just logged.  Narration is generally used to inform
            the user as to what is going on. This can help place errors and
            warnings in context so that they are easier to understand.

        logfile (string or stream or bool):
            May be a string, in which case it is taken to be the path of the
            logfile.  May be *True*, in which case ./.<prog_name>.log is used.
            May be an open stream.  Or it may be *False*, in which case no log
            file is created.

        prog_name (string):
            The program name. Is appended to the message headers and used to
            create the default logfile name. May be a string, in which case it
            is used as the name of the program.  May be *True*, in which case
            *basename(argv[0])* is used.  May be *False* to indicate that
            program name should not be added to message headers.

        argv (list of strings):
            System command line arguments (logged). By default, *sys.argv* is
            used.  If *False* is passed in, *argv* is not logged and *argv[0]*
            is not available to be the program name.

        version (string):
            program version (logged if provided).

        termination_callback (func):
            A function that is called at program termination.

        colorscheme (*None*, 'light', or 'dark'):
            Color scheme to use. *None* indicates that messages should not be
            colorized. Colors are not used if desired output stream is not
            a TTY.

        flush (bool):
            Flush the stream after each write. Is useful if you program is
            crashing, causing loss of the latest writes. Can cause programs to
            run considerably slower if they produce a lot of output. Not
            available with python2.

        stdout (stream):
            Messages are sent here by default. Generally used for testing. If
            not given, *sys.stdout* is used.

        stderr (stream):
            Termination messages are sent here by default. Generally used for
            testing.  If not given, *sys.stderr* is used.

        length_thresh (integer):
            Split header from body if line length would be greater than
            threshold.

        culprit_sep (string):
            Join string used for culprit collections. Default is ', '.

        stream_policy (string or func):
            The default stream policy, which determines which stream each
            informant uses by default (which stream is used if the stream is not
            specifically specified when the informant is created).

            The following named policies are available:
                'termination':
                    stderr is used for the final termination message.
                    stdout is used otherwise.
                    This is generally used for programs are not filters (the
                    output is largely status rather than data that might be fed
                    into another program through a pipeline).
                'header':
                    stderr is used for all messages with headers/severities.
                    stdout is used otherwise.
                    This is generally used for programs are filters (the
                    output is largely data that might be fed into another
                    program through a pipeline). In this case stderr is used for
                    error messages so they do not pollute the data stream.

            May also be a function that returns the stream and takes three
            arguments: the active informant, Inform's stdout, and Inform's
            stderr.

            If no stream is specified, either explicitly on the informant when
            it is defined, or through the stream policy, then Inform's stdout
            is used.

        notify_if_no_tty (bool):
            If it appears that an error message is expecting to displayed on the
            console but the standard output is not a TTY send it to the notifier
            if this flag is True.

        notifier (str):
            Command used to run the notifier. The command will be called with
            two arguments, the header and the body of the message.

        \**kwargs:
            Any additional keyword arguments are made attributes that are
            ignored by *Inform*, but may be accessed by the informants.
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
        culprit_sep=', ',
        stream_policy='termination',
        notify_if_no_tty=False,
        notifier=NOTIFIER,
        **kwargs
    ):
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
        if is_str(stream_policy):
            self.stream_policy = STREAM_POLICIES[stream_policy]
        else:
            self.stream_policy = stream_policy
        self.notifier = notifier
        self.notify_if_no_tty = notify_if_no_tty

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
            argv = getattr(sys, 'argv', None)
        self.output_prog_name = bool(prog_name)
        if argv and not is_str(prog_name):
            prog_name = os.path.basename(argv[0])
        if prog_name is True:
            prog_name = None
        self.prog_name = prog_name
        self.argv = argv

        # Save the color scheme
        assert colorscheme in [None, 'light', 'dark']
        self.colorscheme = colorscheme

        # Activate the actions
        global INFORMER
        self.previous_informer = INFORMER
        INFORMER = self

        # activate the logfile
        self.set_logfile(logfile)

    # __getattr__ {{{2
    def __getattr__(self, name):
        # returns the attribute value if provided otherwise returns None
        # This is generally used by informants to determine whether an extra
        # value was passed to informer.
        if name.startswith('__'):
            raise AttributeError(name)
        return self.__dict__.get(name)

    # suppress_output {{{2
    def suppress_output(self, mute=True):
        """Allows you to change the mute flag (only available as a method).

        Args:
            mute (bool):
                If *mute* is True all output is suppressed (it is still logged).
        """
        self.mute = bool(mute)

    # set_logfile {{{2
    def set_logfile(self, logfile, encoding='utf-8'):
        """Allows you to change the logfile (only available as a method).

        Args:
            logfile:
                May be a string, in which case it is taken to be the path of the
                logfile.  May be *True*, in which case ./.<prog_name>.log is
                used.  May be an open stream.  Or it may be *False*, in which
                case no log file is created.
            encoding (string):
                The encoding to use when writing the file.
        """
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
        if self.argv is None:
            # self.argv may be None, False or a list. None implies that argv was
            # not available when inform was first loaded (as when loaded from
            # sitecustomize.py). False implies it should not be logged.
            self.argv = sys.argv
        if self.argv:
            log("Invoked as '%s'%s." % (' '.join(self.argv), now))
        elif now:
            log("Invoked%s." % now)

    # flush_logfile {{{2
    def flush_logfile(self):
        "Flush the logfile."
        if self.logfile:
            self.logfile.flush()

    # set_stream_policy {{{2
    def set_stream_policy(self, stream_policy):
        "Allows you to change the stream policy (see :class:`inform.Inform`)."
        if is_str(stream_policy):
            self.stream_policy = STREAM_POLICIES[stream_policy]
        else:
            self.stream_policy = stream_policy

    # _report {{{2
    def _report(self, args, kwargs, action):

        # handle continuations
        is_continuation = action.is_continuation
        if is_continuation:
            action = self.previous_action
            assert(action)
        else:
            if action.is_error:
                self.errors += 1

        # assemble the message
        if action._produce_output(self):
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
            if action._write_output(self):
                cs = self.colorscheme if Color.isTTY(options['file']) else None
                self._show_msg(
                    header_color(header, scheme=cs) if header else header,
                    header_color(culprit, scheme=cs) if culprit else culprit,
                    messege_color(message, scheme=cs) if message else message,
                    multiline,
                    options
                )
            notify_override = (
                options['file'] in [self.stdout, self.stderr]   and
                not Color.isTTY()                               and
                (self.notify_if_no_tty and not is_continuation) and
                action.severity
            )
            if action._write_logfile(self) and self.logfile:
                options['file'] = self.logfile
                self._show_msg(
                    header,
                    culprit,
                    Color.strip_colors(message),
                    multiline,
                    options
                )

            if action._notify_user(self) or notify_override:
                import subprocess
                body = ': '.join(cull([culprit, message]))
                subprocess.call(cull([self.notifier, header, body]))
        if action.terminate is not False:
            self.terminate(status=action.terminate)
        self.previous_action = action

    # _get_print_options {{{2
    def _get_print_options(self, kwargs, action):
        opts = dict(
            end=kwargs.get('end', '\n'),
            flush=kwargs.get('flush', self.flush),
        )
            # sep is handled in _render_message
        if sys.version[0] == '2':
            opts.pop('flush')  # flush is not supported in python2
        if 'file' in kwargs:
            opts['file'] = kwargs['file']
        else:
            opts['file'] = self.stream_policy(action, self.stdout, self.stderr)
        return opts

    # _render_message {{{2
    @staticmethod
    def _render_message(args, kwargs):
        return _join(args, kwargs)

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

    # _show_msg {{{2
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
        "Terminate the program with normal exit status."
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
        """Terminate the program with specified exit status.

        Args:
            status (int or string):
                The desired exit status or exit message.

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
        """Terminate the program if error count is nonzero.

        Args:
            status (int or string):
                The desired exit status or exit message.
        """

        if self.errors:
            self.terminate(status)

    # errors_accrued {{{2
    def errors_accrued(self, reset=False):
        """Returns number of errors that have accrued.

        Args:
            reset (bool):
                Reset the error count to 0 if *True*.
        """
        count = self.errors
        if reset:
            self.errors = 0
        return count

    # get_prog_name {{{2
    def get_prog_name(self):
        """Returns the program name."""
        return self.prog_name

    # disconnect {{{2
    def disconnect(self):
        "Disconnect informer, returning to previous informer."
        if self.logfile:
            self.logfile.flush()
        global INFORMER
        if self.previous_informer:
            INFORMER = self.previous_informer
        else:
            INFORMER = DEFAULT_INFORMER

    # __enter__ {{{2
    def __enter__(self):
        return self

    # __exit__ {{{2
    def __exit__(self, type, value, traceback):
        self.disconnect()


# Direct access to class methods {{{1
# done {{{3
def done():
    """Terminate the program with normal exit status.

    Calls :meth:`inform.Inform.done` for the active informer.
    """
    INFORMER.done()


# terminate {{{3
def terminate(status=True):
    """Terminate the program with specified exit status."

    Calls :meth:`inform.Inform.terminate` for the active informer.
    """
    INFORMER.terminate(status)


# terminate_if_errors {{{3
def terminate_if_errors(status=1):
    """Terminate the program if error count is nonzero."

    Calls :meth:`inform.Inform.terminate_if_errors` for the active informer.
    """
    INFORMER.terminate_if_errors(status)


# errors_accrued {{{3
def errors_accrued(reset=False):
    """Returns number of errors that have accrued."

    Calls :meth:`inform.Inform.errors_accrued` for the active informer.
    """
    return INFORMER.errors_accrued(reset)


# get_prog_name {{{3
def get_prog_name():
    """Returns the program name.

    Calls :meth:`inform.Inform.get_prog_name` for the active informer.
    """
    return INFORMER.get_prog_name()


# get_informer {{{3
def get_informer():
    """Returns the active informer."""
    return INFORMER


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

    def get_message(self, template=None):
        """Get exception message.

        Args:
            template (str):
                This argument is treated as a format string and is passed both
                the unnamed and named arguments. The resulting string is treated
                as the message and returned.

                If not specified, the *template* keyword argument passed to the
                exception is used. If there was no *template* argument, then the
                positional arguments of the exception are joined using *sep* and
                that is returned.

        Returned:
            The formatted message without the culprits.
        """
        if template:
            kwargs = self.kwargs.copy()
            kwargs.update(dict(template=template))
        else:
            kwargs = self.kwargs
        return _join(self.args, kwargs)

    def get_culprit(self):
        """Get exception culprit.

        If the *culprit* keyword argument was specified as a string, it is
        returned. If it was specified as a collection, the members are converted
        to strings and joined with *culprit_sep*. The resulting string is
        returned.
        """

        culprit = self.kwargs.get('culprit')
        if is_collection(culprit):
            return ', '.join(str(c) for c in culprit if c is not None)
        elif culprit:
            return str(culprit)

    def report(self, template=None):
        """Report exception.

        The :func:`inform.error` function is called with the exception arguments.

        Args:
            template (str):
                This argument is treated as a format string and is passed both
                the unnamed and named arguments. The resulting string is treated
                as the message and returned.

                If not specified, the *template* keyword argument passed to the
                exception is used. If there was no *template* argument, then the
                positional arguments of the exception are joined using *sep* and
                that is returned.
        """
        if template:
            kwargs = self.kwargs.copy()
            kwargs.update(dict(template=template))
        else:
            kwargs = self.kwargs
        error(*self.args, **kwargs)

    def terminate(self, template=None):
        """Report exception and terminate.

        The :func:`inform.fatal` function is called with the exception arguments.

        Args:
            template (str):
                This argument is treated as a format string and is passed both
                the unnamed and named arguments. The resulting string is treated
                as the message and returned.

                If not specified, the *template* keyword argument passed to the
                exception is used. If there was no *template* argument, then the
                positional arguments of the exception are joined using *sep* and
                that is returned.
        """
        if template:
            kwargs = self.kwargs.copy()
            kwargs.update(dict(template=template))
        else:
            kwargs = self.kwargs
        fatal(*self.args, **kwargs)

    def render(self, template=None):
        """Convert exception to a string for use in an error message.

        Args:
            template (str):
                This argument is treated as a format string and is passed both
                the unnamed and named arguments. The resulting string is treated
                as the message and returned.

                If not specified, the *template* keyword argument passed to the
                exception is used. If there was no *template* argument, then the
                positional arguments of the exception are joined using *sep* and
                that is returned.
        """
        message = self.get_message(template)
        culprit = self.get_culprit()
        return "%s: %s" % (culprit, message) if culprit else message

    def __str__(self):
        return self.render()

    def __getattr__(self, name):
        # returns the value associated with name in kwargs if it exists,
        # otherwise None
        if name.startswith('__'):
            raise AttributeError(name)
        return self.kwargs.get(name)
