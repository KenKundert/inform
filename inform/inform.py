# Inform
# encoding: utf8
#
# Utilities for communicating directly with the user.
# Documentation can be found at inform.readthedocs.io.
#
# Copyright (c) 2014-2024 Kenneth S. Kundert
# This software is licensed under the `MIT Licents <https://mit-license.org>`_.

# Imports {{{1
import arrow
import io
import os
import re
import sys
from codecs import open
from textwrap import dedent as tw_dedent, fill

# Globals {{{1
__version__ = '1.34'
__released__ = '2025-05-10'
INFORMER = None
NOTIFIER = 'notify-send'
STREAM_POLICIES = {
    'termination': lambda i, so, se: se if i.terminate else so,
        # stderr is used on final termination message
    'header': lambda i, so, se: se if i.severity else so,
        # stderr is used on all messages that include headers
    'errors': lambda i, so, se: se if i.is_error else so,
        # stderr is used on all errors
    'all': lambda i, so, se: se,
        # stderr is used for all informants that do not explicitly set stream
        # by default no informants explicitly set stream
}
BAR_CHARS = '▏▎▍▌▋▊▉█'
NUM_BAR_CHARS = len(BAR_CHARS)

"""
These are used to configure inform for doctests:

>>> from inform import Inform, Info, plural, truth
>>> inform = Inform(prog_name=False, logfile=False)

"""

# Inform Utilities {{{1
# _print {{{2
def _print(*args, **kwargs):
    "This is the system print function with handling for BrokenPipeError"
    try:
        print(*args, **kwargs)
    except BrokenPipeError:  # pragma: no cover
        # try to ignore further writing to this stream to avoid another BPE
        stream = kwargs.get('file', sys.stdout)
        if stream == sys.stdout:
            sys.stdout = None
        elif stream == sys.stderr:
            sys.stderr = None
        raise

# get_datetime {{{2
def get_datetime():
    now = arrow.now()
    try:
        return now.strftime("%A, %-d %B %Y at %-I:%M:%S %p %Z")
    except ValueError:  # pragma: no cover
        # there are variations between the implementations of strftime()
        return str(now)

# indent {{{2
def indent(text, leader='    ', first=0, stops=1, sep='\n'):
    r"""Add indentation.

    Args:
        leader (string):
            the string added to be beginning of a line to indent it.

        first (integer):
            number of indentations for the first line relative to others (may be
            negative but (first + stops) should not be).

        stops (integer):
            number of indentations (number of leaders to add to the beginning of
            each line).

        sep (string):
            the string used to separate the lines

    **Example**::

        >>> from inform import display, indent
        >>> display(indent('And the answer is ...\n42!', first=-1))
        And the answer is ...
            42!

    """
    # do the indent
    indented = (first+stops)*leader + (sep+stops*leader).join(str(text).split('\n'))

    # resplit and rejoin while replacing blank lines with empty lines
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

    **Example**::

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
        try:
            return collection.__class__(values)
        except TypeError:
            # this occurs when collection is dict_keys or dict_values
            return values


# is_str {{{2
def is_str(arg):
    """Identifies strings in all their various guises.

    Returns *True* if argument is a string.

    **Example**::

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

    **Example**::

        >>> from inform import is_iterable
        >>> is_iterable('abc')
        True

        >>> is_iterable(['a', 'b', 'c'])
        True

    """
    from collections.abc import Iterable
    return isinstance(obj, Iterable)


# is_collection {{{2
def is_collection(obj):
    """Identifies objects that can be iterated over, excluding strings.

    Returns *True* if argument is a collection (tuple, list, set or dictionary).

    **Example**::

        >>> from inform import is_collection
        >>> is_collection('')  # string
        False

        >>> is_collection([])  # list
        True

        >>> is_collection(())  # tuple
        True

        >>> is_collection({})  # dictionary
        True

        >>> is_collection(set())  # set
        True

    """
    return is_iterable(obj) and not is_str(obj)

# is_array {{{2
def is_array(obj):
    """Identifies objects that are is_array (tuples and arrays).

    Returns *True* if argument is a sequence (tuple or list).

    **Example**::

        >>> from inform import is_array
        >>> is_array('')  # string
        False

        >>> is_array([])  # list
        True

        >>> is_array(())  # tuple
        True

        >>> is_array({})  # dictionary
        False

        >>> is_array(set())  # set
        False

    """
    from collections.abc import Sequence
    return isinstance(obj, Sequence) and not is_str(obj)


# is_mapping {{{2
def is_mapping(obj):
    """Identifies objects that are mappings (are dictionary like).

    Returns *True* if argument is a mapping.

    **Example**::

        >>> from inform import is_mapping
        >>> is_mapping('')  # string
        False

        >>> is_mapping([])  # list
        False

        >>> is_mapping(())  # tuple
        False

        >>> is_mapping({})  # dictionary
        True

    """
    from collections.abc import Mapping
    return isinstance(obj, Mapping)

# Color class {{{2
class Color:
    # description {{{3
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
        enable (bool):
            If set to False, the colorizer does not render the text in color.

    **Example**::

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

    # constants {{{3
    COLORS = 'black red green yellow blue magenta cyan white'.split()
        # The order of the above colors must match order
        # of the standard terminal
    COLOR_CODE_REGEX = re.compile('\033' + r'\[[01](;\d\d)?m')

    # constructor {{{3
    def __init__(self, color, *, scheme=True, enable=True):
        self.color = color
        self.scheme = scheme
        self.enable = enable

    # __call__ {{{3
    def __call__(self, *args, **kwargs):
        text = _join(args, kwargs)
        if not text:
            return text

        # scheme is acting as an override, and False prevents the override.
        scheme = kwargs.get('scheme', self.scheme)
        if scheme is True:
            scheme = INFORMER.colorscheme
        if scheme and self.color and self.enable:
            color = self.color.lower()
            assert color in self.COLORS, f'{color} is an invalid color'
            bright = 1 if scheme == 'light' else 0
            prefix = '\033[%s;3%dm' % (bright, self.COLORS.index(color))
            suffix = '\033[0m'
            return prefix + text + suffix
        return text

    # isTTY {{{3
    @staticmethod
    def isTTY(stream=sys.stdout):
        """Takes a stream as an argument and returns true if it is a TTY.

        Args:
            stream (stream):
                Stream to test.  If not given, *stdout* is used as the stream.

        **Example**::

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

    # strip_colors {{{3
    @classmethod
    def strip_colors(cls, text):
        """Takes a string as its input and return that string stripped of any color codes."""
        if '\033' in text:
            return cls.COLOR_CODE_REGEX.sub('', text)
        return text

    # __repr {{{3
    def __repr__(self):
        return f'{self.__class__.__name__}({self.color!r}, scheme={self.scheme})'


# LoggingCache class {{{2
class LoggingCache:
    # description {{{3
    """LoggingCache

    Use as logfile if you cannot know the desired location of the logfile until
    after log messages have been emitted.  It holds the log messages in memory
    until you establish a logfile.  At that point the messages are copied into
    the logfile.

    **Example**::

        >>> from inform import Inform, LoggingCache, log, indent
        >>> with Inform(logfile=LoggingCache()) as inform:
        ...     log("This message is cached.")
        ...     inform.set_logfile(".mylog")
        ...     log("This message is not cached.")

        >>> with open(".mylog") as f:
        ...     print("Contents of logfile:")
        ...     print(indent(f.read()), end='')  # +ELLIPSIS
        Contents of logfile:
            ...: invoked as: ...
            ...: log opened on ...
            This message is cached.
            This message is not cached.

    """

    # methods {{{3
    def open(self, mode='w', encoding='utf-8'):
        self.log = io.StringIO()
        return self

    def write(self, text):
        self.log.write(text)

    def flush(self):  # pragma: no cover
        pass

    def drain(self):
        return self.log.getvalue()

    def close(self):
        self.log.close()


# User Utilities {{{1
# Info class {{{2
class Info:
    """Generic Data Structure Class

    When instantiated, it converts the provided keyword arguments to attributes.  
    Unknown attributes evaluate to None.

    **Example**::

        >>> class Orwell(Info):
        ...     pass

        >>> george = Orwell(peace='war', freedom='slavery', ignorance='strength')
        >>> print(str(george))
        Orwell(
            peace='war',
            freedom='slavery',
            ignorance='strength',
        )

        >>> george.peace
        'war'

        >>> george.happiness

    """
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def _inform_get_kwargs(self):
        return {k:v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return self.__dict__.get(name)

    def get(self, name, default=None):
        return self.__dict__.get(name, default)

    def render(self, template):
        """Render class to a string

        Args:
            template (str):
                The template string is returned with any instances of {name}
                replaced by the value of the corresponding attribute.

        **Example**::

            >>> george.render('Peace is {peace}. Freedom is {freedom}. Ignorance is {ignorance}.')
            'Peace is war. Freedom is slavery. Ignorance is strength.'

        """

        return template.format(**self.__dict__)

    def __repr__(self):
        return render(self)


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

        wrap (bool or int):
            If true the string is wrapped using a width of 70. If an integer value
            is passed, is used as the width of the wrap.

    **Examples**::

        >>> from inform import join
        >>> join('a', 'b', 'c', x='x', y='y', z='z')
        'a b c'

        >>> join('a', 'b', 'c', x='x', y='y', z='z', template='{2} {z}')
        'c z'

    """
    # _join does not process end, so do it explicitly
    return _join(args, kwargs) + kwargs.get('end', '')


# _join {{{2
def _join(args, kwargs):
    # build the message from the arguments
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

    # wrap the message if desired
    wrap = kwargs.get('wrap')
    if wrap:
        if type(wrap) is int:
            message = fill(message, width=wrap)
        else:
            message = fill(message)
    return message


# render {{{2
_level = 0
_sort = None
def render(obj, sort=None, level=None, tab='    '):
    """Recursively convert object to string with reasonable formatting.

    Args:
        obj:
            The object to render
        sort (bool):
            Dictionary keys and set values are sorted if *sort* is *True*.
            Sometimes this is not possible because the values are not
            comparable, in which case *render* reverts to using the natural
            order.
        level (int):
            The indent level.
            If not specified and render is called recursively the indent
            will be incremented, otherwise the indent is 0.
        tab (string):
            The string used when indenting.

    *render* has built in support for the base Python types (*None*, *bool*,
    *int*, *float*, *str*, *set*, *tuple*, *list*, and *dict*).  If you confine
    yourself to these types, the output of render can be read by the Python
    interpreter.  Other types are converted to string with *repr()*.

    **Example**::

        >>> from inform import display, render
        >>> display('result =', render({'a': (0, 1), 'b': [2, 3, 4]}))
        result = {'a': (0, 1), 'b': [2, 3, 4]}

    In addition, you can add support for render to your classes by adding one or
    both of these methods:

        _inform_get_args(): returns a list of argument values.

        _inform_get_kwargs(): returns a dictionary of keyword arguments.

    **Example**::

        >>> class Chimera:
        ...     def __init__(self, *args, **kwargs):
        ...         self.args = args
        ...         self.kwargs = kwargs
        ...
        ...     def _inform_get_args(self):
        ...         return self.args
        ...
        ...     def _inform_get_kwargs(self):
        ...         return self.kwargs

        >>> lycia = Chimera('Lycia', front='lion', middle='goat', tail='snake')
        >>> display(render(lycia))
        Chimera(
            'Lycia',
            front='lion',
            middle='goat',
            tail='snake',
        )

    """
    # In order for render to be usable in __repr__ functions it must retain the
    # value of the sort and level arguments from previous calls, but the
    # (sort, level) must be returned to (None, 0) after the original call.  If
    # not, subsequent calls to render will the values of sort and level set in
    # previous calls.  To avoid that, we must not allow without resetting the
    # saved versions (_sort, _level) to their previous values. That naturally
    # will not happen if the function returns normally.  In addition, it is
    # important to guard against exceptions from allowing the function to
    # terminate without resetting the saved version to their previous values.
    # This is accomplished using the try/finally block.

    # define sort function, make it either sort or not based on sort
    global _sort
    prev_sort = _sort
    if sort is None:
        sort = sys.version_info < (3, 6) or _sort
    _sort = sort
    if sort:
        def order(keys):
            try:
                return sorted(keys)
            except TypeError:
                # keys are not homogeneous, cannot sort
                return keys
    else:
        def order(keys):
            return keys

    # define function for computing the amount of indentation needed
    def leader(relative_level=0):
        return (level+relative_level)*tab

    # determine the level
    global _level
    prev_level = _level
    if level is None:
        level = _level
    else:
        _level = level

    try:
        if isinstance(obj, dict):
            endcaps = '{ }'
            content = [
                '%r: %s' % (k, render(obj[k], sort, level+1))
                for k in order(obj)
            ]
        elif isinstance(obj, list):
            endcaps = '[ ]'
            content = [render(v, sort, level+1) for v in obj]
        elif isinstance(obj, tuple):
            endcaps = '( ,)' if len(obj) == 1 else '( )'
            content = [render(v, sort, level+1) for v in obj]
        elif isinstance(obj, set):
            endcaps = '{ }'
            content = [render(v, sort, level+1) for v in order(obj)]
        elif hasattr(obj, '_inform_get_args') or hasattr(obj, '_inform_get_kwargs'):
            args = []
            kwargs = {}
            if hasattr(obj, '_inform_get_args') and obj._inform_get_args:
                args = obj._inform_get_args()
            if hasattr(obj, '_inform_get_kwargs') and obj._inform_get_kwargs:
                kwargs = obj._inform_get_kwargs()
            endcaps = '{}( )'.format(obj.__class__.__name__)
            content = (
                [render(v, sort, level+1) for v in args] +
                [n + '=' + render(v, sort, level+1) for n, v in kwargs.items()]
            )
        elif is_str(obj) and '\n' in obj:
            endcaps = None
            content = [
                '"""' + ('\\\n' if obj[0] != '\n' else ''),
                indent(tw_dedent(obj), leader(1)),
                ('' if obj[-1] == '\n' else '\\\n') + leader(0) + '"""'
            ]
            content = [''.join(content)]
        else:
            endcaps = None
            content = [repr(obj)]
    finally:
        # restore level and sort
        _level = prev_level
        _sort = prev_sort

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
    """Similar to ''.format(), but it can pull arguments from the local scope.

    Convert a message with embedded attributes to a string. The values for the
    attributes can come from the argument list, as with ''.format(), or they
    may come from the local scope (found by introspection).

    **Examples**::

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


# dedent {{{2
def dedent(text, strip_nl=None, *, bolm=None, wrap=False):
    """
    Removes indentation that is common to all lines.

    Without its named arguments, dedent behaves just like, and is a equivalent
    replacement for, textwrap.dedent.

    bolm (str):
        The beginning of line mark (bolm) is replaced by a space after the 
        indent is removed.  It must be the first non-space character after
        the initial newline.  Normally bolm is a single character, often '|',
        but it may be contain multiple characters, all of which are replaced by
        spaces.

    strip_nl = None:
        strip_nl is used to strip off a single leading or trailing newline.
        strip_nl may be None, 'l', 't', or 'b' representing neither, leading,
        trailing, or both. True may also be passed, which is equivalent to 'b'.
        Can also use 's' (start) as synonym for 'l' and 'e' (end) or 'r' (right)
        as synonym for 't'.

    wrap (bool or int):
        If true the string is wrapped using a width of 70. If an integer value
        is passed, is used as the width of the wrap.

    >>> from inform import dedent

    >>> print(dedent('''
    ...     ◊   Diaspar
    ...         Lys
    ... ''', bolm='◊'))
    <BLANKLINE>
        Diaspar
        Lys
    <BLANKLINE>

    >>> print(dedent('''
    ...     |   Diaspar
    ...     |   Lys
    ... ''', bolm='|', strip_nl='e'))
    <BLANKLINE>
        Diaspar
    |   Lys

    >>> print(dedent('''
    ...     ||  Diaspar
    ...         Lys
    ... ''', bolm='||', strip_nl='s'))
        Diaspar
        Lys
    <BLANKLINE>

    >>> print(dedent('''
    ...         Diaspar
    ...         Lys
    ... ''', strip_nl='b'))
    Diaspar
    Lys

    >>> print(dedent('''
    ...         Diaspar
    ...         Lys
    ... ''', strip_nl='b', wrap=True))
    Diaspar Lys

    """

    # perform normal dedent
    dedented = tw_dedent(text)

    # remove beginning-of-line-marker if present
    if bolm is not None:
        l = len(bolm) + 1
        if dedented[0:l] == '\n' + bolm:
            dedented = '\n' + ' '*len(bolm) + dedented[l:]

    # remove leading newline if desired
    if strip_nl in ['s', 'b', 'l', True] and dedented[:1] == '\n':
        dedented = dedented[1:]

    # remove trailing newline if desired
    if strip_nl in ['e', 'b', 't', 'r', True] and dedented[-1:] == '\n':
        dedented = dedented[:-1]

    # wrap text to desired width
    if wrap:
        dedented = fill(dedented, wrap) if type(wrap) is int else fill(dedented)

    return dedented


# os_error {{{2
# Generates a reasonable error message for an operating system errors, those
# generated by OSError and its ilk.
def os_error(e):
    """Generates clean messages for operating system errors.

    Args:
        e (exception):
            The value of an *OSError* exception.

    **Example**::

        >>> from inform import display, os_error
        >>> try:
        ...     with open('config') as f:
        ...         contents = f.read()
        ... except OSError as e:
        ...     display(os_error(e))
        config: no such file or directory.

    """

    filenames = ' -> '.join(
        cull([e.filename, getattr(e, 'filename2', None)])
    )
    text = e.strerror.lower() if e.strerror else str(e)
    msg = ': '.join(cull([filenames, text]))
    return full_stop(msg)


# conjoin {{{2
# Like string join method, but supports conjunction
def conjoin(iterable, conj=' and ', sep=', ', end='', fmt=None):
    r"""Conjunction join.

    Args:
        iterable (list or generator of strings):
            The collection of items to be joined. All items are converted to
            strings.
        conj (string):
            The separator used between the next to last and last values.
        sep (string):
            The separator to use when joining the strings in *iterable*.
        end (string):
            Is added to the end of the returned string.
        fmt (string):
            A format string used to convert each item in *iterable* to a string.
            May be a function, in which case it called on each member of
            *iterable* and must return a string.
            If *fmt* is not given, str() is used.

    Return the items of the *iterable* joined into a string, where *conj* is
    used to join the last two items in the list, and *sep* is used to join the
    others.

    **Examples**::

        >>> from inform import conjoin, display, Info
        >>> display(conjoin([], ' or '))
        <BLANKLINE>

        >>> display(conjoin(['a'], ' or '))
        a

        >>> display(conjoin(['a', 'b'], ' or '))
        a or b

        >>> display(conjoin(['a', 'b', 'c']))
        a, b and c

        >>> display(conjoin([10.1, 32.5, 16.9], fmt='${:0.2f}'))
        $10.10, $32.50 and $16.90

        >>> characters = dict(
        ...     bob = 'bob@btca.com',
        ...     ted = 'ted@btca.com',
        ...     carol = 'carol@btca.com',
        ...     alice = 'alice@btca.com',
        ... )
        >>> display(conjoin(characters.items(), fmt='{0[0]:>7} : <{0[1]}>', conj='\n', sep='\n'))
            bob : <bob@btca.com>
            ted : <ted@btca.com>
          carol : <carol@btca.com>
          alice : <alice@btca.com>

        >>> characters = [
        ...     dict(name='bob', email='bob@btca.com'),
        ...     dict(name='ted', email='ted@btca.com'),
        ...     dict(name='carol', email='carol@btca.com'),
        ...     dict(name='alice', email='alice@btca.com'),
        ... ]
        >>> display(conjoin(characters, fmt="{0[name]:>7} : <{0[email]}>", conj=', or\n', sep=',\n', end='.'))
            bob : <bob@btca.com>,
            ted : <ted@btca.com>,
          carol : <carol@btca.com>, or
          alice : <alice@btca.com>.

        >>> characters = [
        ...     Info(name='bob', email='bob@btca.com'),
        ...     Info(name='ted', email='ted@btca.com'),
        ...     Info(name='carol', email='carol@btca.com'),
        ...     Info(name='alice', email='alice@btca.com'),
        ... ]
        >>> display(conjoin(characters, fmt='{0.name:>7} : <{0.email}>', conj='; &\n', sep=';\n', end='.'))
            bob : <bob@btca.com>;
            ted : <ted@btca.com>;
          carol : <carol@btca.com>; &
          alice : <alice@btca.com>.

        >>> display(conjoin(characters, fmt=lambda a: f'{a.name:>7} : <{a.email}>', conj='\n', sep='\n'))
            bob : <bob@btca.com>
            ted : <ted@btca.com>
          carol : <carol@btca.com>
          alice : <alice@btca.com>

    """
    if fmt:
        if callable(fmt):
            lst = [fmt(m) for m in iterable]
        else:
            lst = [fmt.format(m) for m in iterable]
    else:
        lst = [str(m) for m in iterable]
    if conj and len(lst) > 1:
        lst = lst[0:-2] + [lst[-2] + conj + lst[-1]]
    return sep.join(lst) + end

# title_case {{{2
def title_case(
    s,
    exceptions = (
        'and', 'or', 'nor', 'but', 'a', 'an', 'and', 'the', 'as', 'at', 'by',
        'for', 'in', 'of', 'on', 'per', 'to'
    )
):
    """Convert to title case

    This is an attempt to provide an alternative to ''.title() that works with 
    acronyms.

    There are several tricky cases to worry about in typical order of importance:

    0. Upper case first letter of each word that is not an 'minor' word.
    1. Always upper case first word.
    2. Do not down case acronyms
    3. Quotes
    4. Hyphenated words: drive-in
    5. Titles within titles: 2001 A Space Odyssey
    6. Maintain leading spacing
    7. Maintain given spacing: This is a test.  This is only a test.

    The following code addresses 0-3 & 7.  It was felt that addressing the
    others would add considerable complexity.  Case 2 was handled by simply
    maintaining all upper case letters in the specified string.

    **Example**::

        >>> from inform import title_case
        >>> cases = '''
        ...     CDC warns about "aggressive" rats as coronavirus shuts down restaurants
        ...     L.A. County opens churches, stores, pools, drive-in theaters
        ...     UConn senior accused of killing two men was looking for young woman
        ...     Giant asteroid that killed the dinosaurs slammed into Earth at ‘deadliest possible angle,’ study reveals
        ...     Maintain given spacing: This is a test.  This is only a test.
        ... '''.strip()

        >>> for case in cases.splitlines():
        ...    print(title_case(case))
        CDC Warns About "Aggressive" Rats as Coronavirus Shuts Down Restaurants
        L.A. County Opens Churches, Stores, Pools, Drive-in Theaters
        UConn Senior Accused of Killing Two Men Was Looking for Young Woman
        Giant Asteroid That Killed the Dinosaurs Slammed Into Earth at ‘Deadliest Possible Angle,’ Study Reveals
        Maintain Given Spacing: This Is a Test.  This Is Only a Test.

    """

    words = s.strip().split(' ')
        # split on single space to maintain word spacing
        # remove leading and trailing spaces -- needed for first word casing

    def upper(s):
        if s:
            if s[0] in '‘“"‛‟' + "'":
                return s[0] + upper(s[1:])
            return s[0].upper() + s[1:]
        return ''

    # always capitalize the first word
    first = upper(words[0])

    return ' '.join([first] + [
        word if word.lower() in exceptions else upper(word)
        for word in words[1:]
    ])


# did_you_mean {{{2
def did_you_mean(invalid_str, valid_strs):
    """Given an invalid string from the user, return the valid string with the most similarity.

    Args:
        invalid_str (string):
            The invalid string given by the user.
        valid_strs (iterable):
            The set of valid strings that the user was expected to choose from.

    **Examples**::

        >>> from inform import did_you_mean
        >>> did_you_mean('cat', ['cat', 'dog'])
        'cat'
        >>> did_you_mean('car', ['cat', 'dog'])
        'cat'
        >>> did_you_mean('car', {'cat': 1, 'dog': 2})
        'cat'

    """
    from difflib import SequenceMatcher
    similarity = lambda x: SequenceMatcher(a=invalid_str, b=x).ratio()
    return max(valid_strs, key=similarity)

# parse_range {{{2
def parse_range(
    items_str,
    cast = int,
    range = lambda a, b: range(a, b+1),
    block_delim = ',',
    range_delim = '-'
):
    """Parse a set of values from a string where commas can be used to separate 
    individual items and hyphens can be used to specify ranges of items.

    Args:
        items_str (str):
            The string to parse.

        cast (callable):
            A function that converts items from the given string to the type 
            that will be returned.  The function will be given a single 
            argument, which will be a string, and should return that same value 
            casted into the desired type.  Note that the casted values will 
            also be used as the inputs for the *range()* function.

        range (callable):
            A function that produces the values implied by a range.  It will be 
            given two arguments: the start and end of a range.  Both arguments 
            will have already been transformed by the *cast()* function, and 
            the first argument is guaranteed to be less than the second.  The 
            function should return an iterable containing all the values in 
            that range, including the start and end values.

        block_delim (str):
            The character used to separate items and ranges.

        range_delim (str):
            The character used to indicate a range.

    Return:
        set: All of the values specified by the given string.

    **Examples**::

        >>> from inform import parse_range
        >>> parse_range('1-3,5')
        {1, 2, 3, 5}
        >>> abc_range = lambda a, b: [chr(x) for x in range(ord(a), ord(b) + 1)]
        >>> parse_range('A-C,E', cast=str, range=abc_range)  # doctest: +SKIP
        {'B', 'E', 'C', 'A'}

    """
    blocks = items_str.split(block_delim)
    indices = set()

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        if range_delim and range_delim in block:
            begin, end = sorted(cast(x) for x in block.split(range_delim))
            indices.update(range(begin, end))

        else:
            indices.add(cast(block))

    return indices


# format_range {{{2
def format_range(
    items,
    diff = lambda a, b: b - a,
    key = None,
    str = str,
    block_delim = ',',
    range_delim = '-',
):
    """Create a string that succinctly represents the given set of items.  
    Groups of consecutive items are succinctly displayed as a range, and other 
    items are listed individually.

    Args:
        items:
            An iterable containing the values to format.  Any type of iterable 
            can be given, but it will always be treated as a set (e.g. order 
            doesn't matter, duplicates are ignored).  By default, the items in 
            the iterable must be non-negative integers, but by customizing the 
            other arguments, it is possible to support any discrete, ordered 
            type.

        key (callable or None):
            A key function used to sort the given values, or None if the values 
            can be sorted directly.

        str (callable):
            A function that can be used to convert an individual value from 
            *items* into a string.

        block_delim (str):
            The character used to separate individual items and ranges in the 
            formatted string.

        range_delim (str):
            The character used to indicate ranges in the formatted string.

    **Examples**::

        >>> from inform import format_range
        >>> format_range([1, 2, 3, 5])
        '1-3,5'
        >>> abc_diff = lambda a, b: ord(b) - ord(a)
        >>> format_range('ACDE', diff=abc_diff)
        'A,C-E'

    """
    blocks = []
    current_seq = []

    def make_block(seq):
        if len(seq) == 0:
            return []
        elif len(seq) == 1:
            return [str(seq[0])]
        elif len(seq) == 2:
            return [str(seq[0]), str(seq[1])]
        else:
            return ['{}{}{}'.format(seq[0], range_delim, seq[-1])]

    for x in sorted(set(items), key=key):
        if current_seq and diff(current_seq[-1], x) != 1:
            blocks += make_block(current_seq)
            current_seq = []
        current_seq.append(x)

    blocks += make_block(current_seq)
    return block_delim.join(blocks)

# plural {{{2
class plural:
    """Conditionally format a phrase depending on the number of things.

    You may provide the count directly by specifying a number (e.g. 0, 1, 2,
    ...) for the value.  Or the value may be an object that implements
    `__len__()` (e.g. list, dict, set, ...) in which case the count is the
    length is taken to be the count.

    You specify a format string to control how the value is converted to a
    string.  The format string can either be included in the format section of a
    Python string expansion or can be specified using the *formatter* argument.
    For example:

        >>> f"{plural(17):# item}"
        '17 items'

        >>> items = plural(17, formatter="# item")
        >>> str(items)
        '17 items'

    The format string has one to four sections separated by '/' with the various
    section being included in the output depending on the count.

        ALWAYS
        ALWAYS/MANY
        ALWAYS/ONE/MANY
        ALWAYS/ONE/MANY/NONE

    The first section, ALWAYS, is always included, the rest are appended to
    ALWAYS as appropriate based on the count.  If no other sections are given,
    then an 's' appended to ALWAYS except when the count is 1.  Otherwise MANY
    is added if the count is two or more.  It is also used if NONE is not given
    and the count is zero.  ONE is added if available and the count is 1.
    Finally NONE is added if available and the value is zero.

    If any of the sections contain a '#', it is replaced by the number of things.

    If the format string starts with an '!' then it is removed and the sense of
    plurality reverses.  The plural form is used if the value is 1 and the
    singular form is used otherwise.  In this situation, NONE is ignored.  This
    is useful when pluralizing verbs.

    **Examples**::

        >>> from inform import plural

        >>> f"{plural(1):thing}, {plural(2):thing}"
        'thing, things'

        >>> f"{plural(1):bush/es}, {plural(2):bush/es}"
        'bush, bushes'

        >>> f"{plural(1):/goose/geese}, {plural(2):/goose/geese}"
        'goose, geese'

        >>> f"{plural(1):# ox/en}, {plural(2):# ox/en}"
        '1 ox, 2 oxen'

        >>> none = plural(0)
        >>> one = plural(1)
        >>> many = plural(9)
        >>> f"{none:/a cactus/# cacti/no cacti}, {one:/a cactus/# cacti/no cacti}, {many:/a cactus/# cacti/no cacti}"
        'no cacti, a cactus, 9 cacti'

        >>> f"{none:!# run}, {one:!# run}, {many:!# run}"
        '0 run, 1 runs, 9 run'

        >>> pronoun = 'He'
        >>> singers = plural(['John'])
        >>> print(f"{singers:/{pronoun}/They} {singers:!sing}.".capitalize())
        He sings.

        >>> singers = plural(['John', 'Paul', 'George', 'Ringo'])
        >>> print(f"{singers:/{pronoun}/They} {singers:!sing}.".capitalize())
        They sing.

    You can specify a function for *render_num* to customize the conversion of
    the count to a string.

        >>> from num2words import num2words

        >>> f"He has {plural(1, render_num=num2words):# /wife/wives}."
        'He has one wife.'

        >>> f"He has {plural(42, render_num=num2words):# /wife/wives}."
        'He has forty-two wives.'

    You can access the originally specified value using the *value* attribute.

        >>> agreement = "{tenants:Tenant} ({names}) {tenants:!agree} to ..."

        >>> tenants = plural(["Hayden Fair"])
        >>> agreement.format(tenants=tenants, names=conjoin(tenants.value))
        'Tenant (Hayden Fair) agrees to ...'

        >>> tenants = plural(["Tawna", "Barbara"])
        >>> agreement.format(tenants=tenants, names=conjoin(tenants.value))
        'Tenants (Tawna and Barbara) agree to ...'

    You can access the number of items using the *count* attribute.

        >>> plural(5).count
        5
        >>> plural(['a', 'b', 'c']).count
        3
        >>> plural(1/2).count
        0.5

    If '/', '#', or '!' are inconvenient, you can change them by passing the
    *slash*, *num* and *invert* arguments to plural().

    Applying str() to a *plural* object uses the *formatter* constructor argument:

        >>> bears = plural(5, formatter="# bear")
        >>> str(bears)
        '5 bears'

    If *default* is not specified, the count is returned:

        >>> str(plural(5))
        '5'

        >>> str(plural(1))
        '1'

        >>> str(plural(0))
        '0'

    The original implementation is from Veedrac on Stack Overflow: 
    http://stackoverflow.com/questions/21872366/plural-string-formatting
    """

    def __init__(self, value, formatter=None, *, render_num=str, num='#', invert='!', slash='/'):
        from collections.abc import Sized

        self.value = value
        self.count = len(value) if isinstance(value, Sized) else value
        self.render_num = render_num
        self.num = num
        self.invert = invert
        self.slash = slash
        if formatter is None:
            formatter = "/#/#/#"
        self.formatter = formatter

    def format(self, formatter=None):
        """Expand plural to a string.

        You can use this method to directly expand plural to a string without
        needing to use f-strings or the string format method.

        **Examples**::

            >>> plural(1).format('thing')
            'thing'
            >>> plural(3).format('/a cactus/# cacti')
            '3 cacti'

        """
        if formatter is None:
            formatter = self.formatter
        return self.__format__(formatter)

    def __format__(self, formatter=None):
        if not formatter:
            formatter = self.formatter

        inverted = formatter[0:1] == self.invert
        if inverted:
            formatter = formatter[1:]

        components = formatter.split(self.slash)
        num_components = len(components)
        always = components[0]
        if num_components == 1:
            singular, plural, none = '', 's', 's'
        elif num_components == 2:
            plural = components[1]
            singular, none = '', plural
        elif num_components >= 3:
            singular = components[1]
            plural = components[2]
            none = plural if num_components == 3 else components[3]
            if num_components > 4:
                raise ValueError("format specification has too many components.")

        if inverted:
            singular, plural, none = plural, singular, singular

        if self.count == 1:
            suffix = singular
        elif self.count == 0:
            suffix = none
        else:
            suffix = plural

        # Don't replace the number symbol until the very end because it's
        # possible that this step could introduce extra separators (e.g. if the
        # number is a fraction).
        out = always + suffix
        return out.replace(self.num, self.render_num(self.count))

    def __str__(self):
        return self.format()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.count})"

# truth {{{2
class truth:
    """Conditionally format a phrase depending on whether it is true or false.

    You specify a format string to control how the value is converted to a
    string.  The format string can either be included in the format section of a
    Python string expansion or can be specified using the *formatter* argument.
    For example:

        >>> f"{truth(True):aye/no}"
        'aye'

        >>> response = truth(True, formatter="aye/no")
        >>> str(response)
        'aye'

    The format string has two sections, separated by '/'.  The first section is
    included only if the given value is true and the last section is included
    only if the given value is false.

    Both sections are optional.  If the last section is not given it is left
    blank.  If both sections are not given, 'yes' is returned for true and 'no'
    for false.

    If either section contains %, it is replaced by the value.

    Converting truth to a Boolean returns True or False.

    **Examples**::

        >>> from inform import truth

        >>> f"account is {truth(True):past due/current}."
        'account is past due.'

        >>> f"account is {truth(False):past due/current}."
        'account is current.'

        >>> paid = truth("20 July 1969")
        >>> is_overdue = truth(True)
        >>> f"last payment: {paid:%/not received}{is_overdue: — overdue}"
        'last payment: 20 July 1969 — overdue'

        >>> paid.format('%')
        '20 July 1969'

        >>> paid = truth(None)
        >>> f"last payment: {paid:%/not received}{is_overdue: — overdue}"
        'last payment: not received — overdue'

        >>> paid.format('%')
        ''

        >>> f"in arrears: {is_overdue}"
        'in arrears: yes'

        >>> bool(is_overdue)
        True

        >>> str(is_overdue)
        'yes'

        >>> in_german = truth(True, formatter="ja/nein")
        >>> str(in_german)
        'ja'

    If '/', or '%' are inconvenient, you can change them by passing the
    *slash* and *interpolate* arguments to truth().
    """

    def __init__(self, value, formatter=None, *, interpolate='%', slash='/'):
        self.value = value
        self.interpolate = interpolate
        self.slash = slash
        if formatter:
            use_if_true, _, use_if_false = formatter.partition(self.slash)
            self.defaults = use_if_true, use_if_false
        else:
            self.defaults = 'yes', 'no'

    def format(self, formatter=None):
        """Expand truth to a string.

        You can use this method to directly expand truth to a string without
        needing to use f-strings or the string format method.

        **Examples**::

            >>> truth(True).format('yes/no')
            'yes'

        """
        return self.__format__(formatter)

    def __format__(self, formatter):
        value = self.value
        if formatter:
            use_if_true, _, use_if_false = formatter.partition(self.slash)
        else:
            use_if_true, use_if_false = self.defaults
        out = use_if_true if bool(value) else use_if_false
        return out.replace(self.interpolate, str(value))

    def __str__(self):
        return self.defaults[0] if self.value else self.defaults[1]

    def __repr__(self):
        return f"{self.__class__.__name__}({bool(self.value)})"

    def __bool__(self):
        return bool(self.value)

# full_stop {{{2
def full_stop(sentence, end='.', allow='.?!', remove=r'\\'):
    """Add period to end of string if it is needed.

    A full stop (a period) is added if there is no terminating punctuation at the
    end of the string.  The argument is first converted to a string, and then
    any white space at the end of the string is removed before looking for
    terminal punctuation.  If the last character is in *allow* then no further
    modifications performed.  If the last character is in *remove*, it is
    removed and no further modifications performed.  Otherwise the *end* is
    appended.  The return value is always a string.

    **Examples**::

        >>> from inform import full_stop
        >>> full_stop('The file is out of date')
        'The file is out of date.'

        >>> full_stop('The file is out of date.')
        'The file is out of date.'

        >>> full_stop('Is the file is out of date?')
        'Is the file is out of date?'

        >>> full_stop(f"invalid character found: {''}§", remove=r'§')
        'invalid character found: '

    You can override the allowed and desired endings::

        >>> cases = '1, 3 9, 12.'.split()
        >>> print(*[full_stop(c, end=',', allow=',.') for c in cases])
        1, 3, 9, 12.

    """
    sentence = str(sentence).rstrip()
    if sentence[-1:] in remove:
        return sentence[:-1]
    return sentence if sentence[-1] in allow else sentence + end


# columns {{{2
def columns(
    array, pagewidth=79, alignment='<', leader='    ',
    min_sep_width=2, min_col_width=1
):
    """Distribute array over enough columns to fill the screen.

    Returns a multiline string.

    Args:
        array (collection of strings):
            The array to be printed.

        pagewidth (int):
            The number of characters available for each line.

        alignment ('<', '^', or '>'):
            Whether to left ('<'), center ('^'), or right ('>') align the
            *array* items in their columns.

        leader (str):
            The string to prepend to each line.

        min_sep_width (int):
            The minimum number of spaces between columns.  Default is 2.

        min_col_width (int):
            The minimum width of a column.  Default is 1.

    **Example**::

        >>> from inform import columns, display, full_stop
        >>> title = 'The NATO phonetic alphabet:'
        >>> words = '''
        ...     Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett
        ...     Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango
        ...     Uniform Victor Whiskey X-ray Yankee Zulu
        ... '''.split()
        >>> newline = '''
        ... '''
        >>> display(title, columns(words), sep=newline)
        The NATO phonetic alphabet:
            Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
            Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
            Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
            Delta     Hotel     Lima      Papa      Tango     X-ray

    """
    array = list(array)
    textwidth = pagewidth - len(leader)
    width = max([len(e) for e in array]) + min_sep_width - 1
    width = max(min_col_width, width)
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


# render bar {{{2
def render_bar(value, width=72, full_width=False):
    """Render graphic representation of a value in the form of a bar

    Args:
        value (real): Should be normalized (fall between 0 and 1)

        width (int): The width of the bar in characters when value is 1.

        full_width (bool):
            Whether bar should be rendered to fill the whole width using
            trailing spaces,.  This is useful if you plan to mark the end of the
            bar.
    **Examples**::

        >>> from inform import render_bar

        >>> assets = {'property': 13_194, 'cash': 2846, 'equities': 19_301}
        >>> total = sum(assets.values())
        >>> for key, value in assets.items():
        ...     display(f"{key:>8}: ❭{render_bar(value/total, full_width=True)}❬")
        property: ❭██████████████████████████▉                                             ❬
            cash: ❭█████▊                                                                  ❬
        equities: ❭███████████████████████████████████████▎                                ❬


    """
    scaled = value*width
    if scaled > width:
        scaled = width
    if scaled < 0:
        scaled = 0
    buckets = int(scaled)
    frac = int((NUM_BAR_CHARS*scaled) % NUM_BAR_CHARS)
    extra = BAR_CHARS[frac-1:frac]
    bar = buckets*BAR_CHARS[-1] + extra
    if full_width:
        bar += (width - len(bar))*' '
    return bar


# tree {{{2
# _gen_connectors {{{3
def _gen_connectors(width):
    space = " "     # This is a non-breaking space, needed with variable width fonts
    line = "─"      # This is horizontal rule
    connector_seeds = dict(
        item = "├",
        last_item = "└",
        lead = "│",
        last_lead = space,
    )
    pad = space if width > 1 else ''

    def extend(seed):
        fill = space if seed in [space, "│"] else line
        # return seed + (width - 2)*fill + pad
        return offset*space + seed + (width - 2 - offset)*fill + pad

    return Info(**{k: extend(v) for k, v in connector_seeds.items()})

nav_width = 4  # the width of the column that holds a vertical bar
offset = 0     # how many spaces to shift the vertical bars to the right
connectors = _gen_connectors(nav_width)

# tree {{{3
def tree(data, squeeze=False):
    """
        Render a data hierarchy as a tree.

        Args:
            data (hierarchy of dictionaries, lists, strings):
                The hierarchy to be rendered.  Keys are converted to strings.
                Falsy values are converted to empty strings.
            squeeze (bool):
                If True, an extra level of hierarchy is not added for string
                values.

        Example:
            >>> from inform import tree

            >>> addresses = {
            ...     "Katheryn McDaniel": {
            ...         'position': 'president',
            ...         'address': '138 Almond Street\nTopeka, Kansas 20697',
            ...         'phone': {
            ...             'cell': '1-210-555-5297',
            ...             'work': '1-210-555-8470',
            ...         },
            ...         'email': 'KateMcD@aol.com',
            ...         'additional roles': [
            ...             'board member',
            ...             'chair of strategy subcommittee'
            ...         ]
            ...     }
            ... }

            >>> print(tree(addresses, squeeze=True))
            Katheryn McDaniel
            ├── position: president
            ├── address: 138 Almond Street
            │            Topeka, Kansas 20697
            ├── phone
            │   ├── cell: 1-210-555-5297
            │   └── work: 1-210-555-8470
            ├── email: KateMcD@aol.com
            └── additional roles
                ├── board member
                └── chair of strategy subcommittee

    """
    return _tree(data, squeeze, top=True)

# _tree {{{3
def _tree(data, squeeze, top=False, leader=''):
    lines = []
    if hasattr(data, 'items'):
        last = len(data) - 1
        for i, item in enumerate(data.items()):
            key, value = item
            key = str(key)
            # determine key-leader-supplement and item-leader-supplement
            if top:
                kls = ''
                ils = ''
            elif i < last:
                kls = connectors.item
                ils = connectors.lead
            else:
                kls = connectors.last_item
                ils = connectors.last_lead

            indented_key = leader + kls + key
            if is_collection(value) or not squeeze:
                # append subhierarchy to those already processed
                lines += [
                    indented_key,
                    _tree(value, squeeze, leader=leader+ils) if value else None
                ]
            else:
                # the value is a scalar, so squeeze key & value on one line
                intro_cont = leader + ils + (len(key)+2)*' '
                if value:
                    v = indent(str(value), leader=intro_cont, first=-1, stops=1)
                    lines += [f"{indented_key}: {v}"]
                else:
                    lines += [indented_key]
        return '\n'.join(l for l in lines if l)

    elif not is_collection(data):
        data = [indent(data, leader=leader + nav_width*' ', stops=1, first=-1)]

    if top:
        joiner = '\n'
        terminator = '\n'
        items = conjoin(data, sep='\n', conj='\n')
    else:
        joiner = '\n' + leader + connectors.item
        terminator = '\n' + leader + connectors.last_item
        connector = connectors.item if len(data) > 1 else connectors.last_item
        items = leader + connector + conjoin(data, sep=joiner, conj=terminator)

    if items:
        lines.append(items)
    return '\n'.join(lines)


# ProgressBar class {{{2
class ProgressBar:
    # description {{{3
    """Draw a progress bar.

    Args:
        stop (float, iterable):
            The last expected value.  May also be an iterable (list, tuple,
            iterator, etc), in which case the ProgressBar becomes an interable
            and start and log are ignored.

        start (float):
            The first expected value. May be greater than or less than stop, but
            it must not equal stop. Must be specified and must be nonzero and
            the same sign as stop if log is True.

        log (bool):
            Report the logarithmic progress (start and stop must be positive and
            nonzero).

        prefix (str):
            A string that is output before the progress bar on the same line.

        width (int):
            The maximum width of the bar, the largest factor of 10 that
            is less than or equal to this value is used.  If width is less than
            or equal to zero, it is added to the current width of the terminal.

        informant (informant):
            Which informant to use when outputting the progress bar.  By
            default, :func:`inform.display()` is used.  Passing *None* or
            *False* as *informant* suppresses the display of the progress bar.

        markers (dict):
            This argument is used to associate a marker name with a pair of
            values, a character and a color.  If a known marker name is passed
            to draw(), the resulting update is rendered using the matching
            fill character and color.  The color may be specified as a string
            (the color name), a Color object, or None (uncolored).

            Markers should be given in order of increasing priority.  If two
            different markers appear on non-printing updates, the one that is
            closer to the end of the dictionary is used on the next printing
            update.

    There are three typical use cases.
    First, use to illustrate the progress through an iterator::

        for item in ProgressBar(items):
            process(item)

    Second, use to illustrate the progress through a fixed number of items::

        for i in ProgressBar(50):
            process(i)

    Lastly, to illustrate the progress through a continuous range::

        stop = 1e-6
        step = 1e-9
        with ProgressBar(stop) as progress:
            value = 0
            while value <= stop:
                progress.draw(value)
                value += step

    It produces a bar that grows in order to indicate progress.  After progress
    is complete, it will have produced the following::

        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0

    It coordinates with the informants so that interruptions are handled cleanly::

        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅
        warning: the sky is falling.
        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0

    This last version can be used to indicate the nature of individual updates.
    This is usually used to signal that there was a problem with the update.
    For example, the following example uses both color and fill character to
    distinguish four types of results: okay, warn, fail, error::

        results = 'okay okay okay fail okay fail okay error warn okay'.split()

        markers = dict(
            okay=('⋅', 'green'),
            warn=('−', 'yellow'),
            fail=('×', 'magenta'),
            error=('!', 'red')
        )
        with ProgressBar(len(results), markers=markers) as progress:
            for i in range(len(repos)):
                result = results[i]
                progress.draw(i+1, result)

    It produces the following, where each of the types is rendered in the
    appropriate color::

        ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7××××××6⋅⋅⋅⋅⋅⋅5××××××4⋅⋅⋅⋅⋅⋅3!!!!!!2−−−−−−1⋅⋅⋅⋅⋅⋅0

    """

    # constructor {{{3
    def __init__(
        self, stop, start=0, *,
        log=False, prefix=None, width=79, informant=True, markers={}
    ):
        if width <= 0:
            try:
                width = os.get_terminal_size().columns + width
            except OSError:
                width=79

        self.override_limits(stop, start, log)

        self.major = width//10
        self.width = 10*self.major
        self.prefix = prefix
        self.informant = display if informant is True else informant
        self.prev_index = 0
        self.started = False
        self.informer = get_informer()

        # prepare for use of markers
        def to_color(c):
            if c:
                return Color(c) if is_str(c) else c
            return lambda c : c
        self.markers = {None: ('⋅', to_color(None))}
        self.markers.update({k:(v[0], to_color(v[1])) for k,v in markers.items()})
        self.prev_marker = None
        self.use_prev_marker = False
        self.previously_shown = ''

    # override_limits() {{{3
    def override_limits(self, stop, start, log):
        """
        Overrides start, stop, and log settings

        Not normally needed. Generally used to give the limits when they are not
        known in advance.  Initiate with bogus limits and use this function to
        override before the first draw operation.
        """
        try:
            self.iterator = stop
            stop = len(stop)
            start = 0
            assert not log
        except TypeError:
            self.iterator = None

        if log:
            from math import log10
            start = log10(start)
            stop = log10(stop)
        self.reversed = start > stop
        if self.reversed:
            start = -start
            stop = -stop
        self.start = start
        self.stop = stop
        self.log = log

        self.finished = stop == start
            # if stop == start, just declare progress bar to be done;
            # doing so avoids the divide by zero problem

    # draw() {{{3
    def draw(self, abscissa, marker=None):
        "Draw the progress bar."
        if self.finished:
            return
        if self.log:
            from math import log10
            abscissa = log10(abscissa)
        if self.reversed:
            abscissa = -abscissa

        assert marker in self.markers, f"{marker}: unknown marker."
        index = int(self.width*(abscissa - self.start)/(self.stop - self.start))

        self._draw(index, marker)
            # Must actually print the bar rather than returning a string because
            # done() also needs to contribute to the output, and it is generally
            # called from __exit__() and so cannot return anything.

    # done() {{{3
    def done(self):
        """Complete the progress bar.

        Not needed if *ProgressBar* is used with the Python *with* statement.
        """
        if self.finished:
            return
        if self.started:
            # complete the bar if it was actually started
            self._draw(self.width, self.prev_marker)
            if self.informant:
                _, color = self.markers[self.prev_marker]
                self.informant(color(0), continuing=True)
        self.finished = True

    # escape() {{{3
    def escape(self):
        """Terminate the progress bar without completing it."""
        if self.finished:
            return
        if self.informant:
            self.informant(continuing=True)
        self.finished = True

    # _draw {{{3
    def _draw(self, index, marker):
        if not self.informant:  # pragma: no cover
            return

        stream_info = self.informer.get_stream_info(self.informant)
        flush = False
        if self.prefix:
            if stream_info.interrupted or not self.started:
                self.informant(self.prefix, end='', continuing=True)
                flush = True
        if stream_info.interrupted:
            self.informant(self.previously_shown, end='', continuing=True)
            flush = True

        # choose the highest priority marker seen since last draw
        resolved_marker = marker
        if self.use_prev_marker:
            # if use_prev_marker is true, it indicates that some unprinted
            # points were received.  This code ups the marker to the most severe
            # received since the last marker was actually printed.
            for resolved_marker in reversed(list(self.markers)):
                if resolved_marker in [marker, self.prev_marker]:
                    break
            else:
                raise AssertionError  # pragma: no cover
        self.prev_marker = resolved_marker
        self.use_prev_marker = True
        fill_char, color = self.markers[resolved_marker]

        text = []
        for i in range(self.prev_index, index):
            if i % self.major == self.major-1:
                K = 9 - i // self.major
                # Don't print final 0 as we may not be finished yet; this
                # occurs in real sweeps.  Terminal 0 added in self.done()
                if K:
                    text.append(str(K))
            else:
                text.append(fill_char)
        if text:
            text = color(''.join(text))
            self.informant(text, end='', continuing=True)
            flush = True

            self.previously_shown += text
            self.use_prev_marker = False
        self.prev_index = index
        stream_info.interrupted = False
        self.started = True
        if flush:
            # something was printed, so flush the stream because an interruption
            # could be printed to stderr, which is not buffered.  If this stream
            # is not flushed the user may see output out of order.
            stream_info.stream.flush()

    # context manager {{{3
    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        if exception:
            self.escape()
        else:
            self.done()

    # __iter__ {{{3
    def __iter__(self):
        if self.iterator is not None:
            iterator = self.iterator
        elif type(self.stop) is int:
            iterator = range(self.start, self.stop+1)
            self.start = 0
            self.log = False
        else:
            raise NotImplementedError('no iterator available')

        for i, each in enumerate(iterator):
            self.draw(i)
            yield each
        self.done()

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

        # highlight_header = Color('magenta', enable=Color.isTTY(sys.stdout))
        # highlight_body = Color('blue', enable=Color.isTTY(sys.stdout))
        # header = 'DEBUG: {fname}:{lineno}, {name}'.format(
        #     fname=fname, lineno=lineno, name=name
        # )
        body = _join(args, kwargs)
        # header += ':\n' if body else '.'
        # message = highlight_header(header) + highlight_body(indent(body))
        debug(body, culprit=(fname, lineno, name))

    finally:
        # Failing to explicitly delete the frame can lead to long-lived
        # reference cycles.
        del frame


def ppp(*args, **kwargs):
    '''Print function.

    Mimics the normal print function, but colors printed output to make it
    easier to see and labels it with the location of the call.
    '''
    frame_depth = 1
    _debug(frame_depth, args, kwargs)


def ddd(*args, **kwargs):
    '''Print arguments function.

    Pretty-prints its arguments. Arguments may be named or unnamed.
    '''
    # if an argument has __dict__ attribute, render that rather than arg itself
    def expand(arg):
        try:
            try:
                name = arg.__class__.__name__ + ' object'
            except AttributeError:  # pragma: no cover
                try:
                    name = arg.__name__
                except AttributeError:
                    return render(arg.__dict__)
            return name + ' containing ' + render(arg.__dict__)
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
    '''Print variables function.

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


def aaa(*args, **kwargs):
    '''Print argument, then return it.

    Pretty-prints its argument. Argument may be named or unnamed.  Allows you to
    display the value that is only contained within an expression.
    '''
    assert len(args) + len(kwargs) == 1
    if args:
        arg = args[0]
        args = [render(arg)]
    else:
        key, arg = kwargs.popitem()
        args = [key, render(arg)]
    frame_depth = 1
    _debug(frame_depth, args, {'sep': ': '})
    return arg


def ccc(*args, **kwargs):
    'Print the class name for all arguments.'
    args = [
        arg.__class__.__name__ for arg in args
    ] + [
        '{k} = {v}'.format(k=k, v=v.__class__.__name__)
        for k, v in sorted(kwargs.items())
    ]
    frame_depth = 1
    _debug(frame_depth, args, kwargs=dict(sep='\n'))


def sss(ignore_exceptions=True):
    """Print a stack trace

    Args:
        ignore_exceptions: (bool)
            If true, the stack trace will exclude the path through exceptions.
    """
    import traceback
    if ignore_exceptions:
        tb = traceback.extract_stack()
    else:
        tb = traceback.extract_tb(sys.exc_info()[2])
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
    """Create informants.

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
            specified, the stream to use will be determined by the stream policy
            of the active informer.

        clone (informant):
            Clone the attributes of the given informer. Any explicitly specified
            arguments override those acquired through cloning.

    **Example**:

        The following generates two informants, *passes*, which prints its
        messages in green, and *fails*, which prints its messages in red.  Output
        to the standard output for both is suppressed if *quiet* is *True*::

            >>> from inform import InformantFactory, display

            >>> success = InformantFactory(
            ...     clone = display,
            ...     severity = 'Pass',
            ...     header_color = 'green'
            ... )
            >>> failure = InformantFactory(
            ...     clone = display,
            ...     severity = 'FAIL',
            ...     header_color = 'red'
            ... )

        *success* and *failure* are both informants. Once created, they can be
        used to give messages to the user::

            >>> results = [
            ...     (0,   0.005, 0.025),
            ...     (0.5, 0.512, 0.025),
            ...     (1,   0.875, 0.025),
            ... ]
            >>> for expected, measured, tolerance in results:
            ...     if abs(expected - measured) > tolerance:
            ...         report = failure
            ...     else:
            ...         report = success
            ...     report(
            ...         measured, expected, measured-expected,
            ...         template='measured = {:.3f}V, expected = {:.3f}V, diff = {:.3f}V'
            ...     )
            Pass: measured = 0.005V, expected = 0.000V, diff = 0.005V
            Pass: measured = 0.512V, expected = 0.500V, diff = 0.012V
            FAIL: measured = 0.875V, expected = 1.000V, diff = -0.125V

        In the console 'Pass' is rendered in green and 'FAIL' in red.
    """

    def __init__(self, **kwargs):
        # set default values
        self.severity = None
        self.is_error = False
        self.log = True
        self.output = True
        self.notify = False
        self.terminate = False
        self.is_continuation = False
        self.message_color = None
        self.header_color = None
        self.stream = None

        # override defaults with values from clone
        clone = kwargs.pop('clone', None)
        if clone:
            self.__dict__.update(clone.__dict__)

        # override with values specified in argument list
        self.__dict__.update(kwargs)
        if not isinstance(self.header_color, Color):
            self.header_color = Color(self.header_color)
        if not isinstance(self.message_color, Color):
            self.message_color = Color(self.message_color)


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
    message_color='blue',
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
    terminate=True,
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
    # description {{{2
    """Inform

    Manages all informants, which in turn handle user messaging.  Generally
    informants copy messages to the logfile while most also send to the standard
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

        logfile (path, string, stream, bool):
            May be a pathlib path or a string, in which case it is taken to be
            the path of the logfile.  May be *True*, in which case
            ./.<prog_name>.log is used.  May be an open stream.  Or it may be
            *False*, in which case no log file is created.  It may also be an
            instance of :class:`LoggingCache`, which caches the log messages
            until it is replaced with :meth:`Inform.set_logfile`.

        prev_logfile_suffix (string):
            If specified, the previous logfile will be moved aside before
            creating the new logfile.

        error_status (int)
            The default exit status to return to the shell when terminating the
            program due to an error.  The default is 1.

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
            A function that is called at program termination. This function is
            called before the logfile is closed and is only called if Inform
            processes the program termination. If you want to register a
            function to run regardless of how the program exit is processed, use
            the atexit module.

        colorscheme (*None*, 'light', or 'dark'):
            Color scheme to use. *None* indicates that messages should not be
            colorized. Colors are not used if desired output stream is not
            a TTY.

        flush (bool):
            Flush the stream after each write. Is useful if your program is
            crashing, causing loss of the latest writes. Can cause programs to
            run considerably slower if they produce a lot of output. Not
            available with python2.

        stdout (stream):
            Messages are sent here by default. Generally used for testing. If
            not given, *sys.stdout* is used.

        stderr (stream):
            Exceptional messages are sent here by default. Exceptional message
            include termination messages and possibly error messages (depends on
            stream_policy). Generally used for testing.  If not given,
            *sys.stderr* is used.

        length_thresh (integer):
            Split header from body if line length would be greater than this
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
                    This is generally used for programs that are not filters
                    (the output is largely status rather than data that might be
                    fed into another program through a pipeline).
                'header':
                    stderr is used for all messages with headers/severities.
                    stdout is used otherwise.
                    This is generally used for programs that act as filters (the
                    output is largely data that might be fed into another
                    program through a pipeline). In this case stderr is used for
                    error messages so they do not pollute the data stream.
                'errors':
                    stderr is used for all errors, stdout is used otherwise.
                    This is also commonly used for programs that act as filters.
                'all':
                    stderr is used for all informants that do not explicitly set stream.
                    By default no informants explicitly set stream.

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

        \\**kwargs:
            Any additional keyword arguments are made attributes that are
            ignored by *Inform*, but may be accessed by the informants.
    """

    # constructor {{{2
    def __init__(
        self,
        mute = False,
        quiet = False,
        verbose = False,
        narrate = False,
        logfile = False,
        prev_logfile_suffix = None,
        error_status = 1,
        prog_name = True,
        argv = None,
        version = None,
        termination_callback = None,
        colorscheme = 'dark',
        flush = False,
        stdout = None,
        stderr = None,
        length_thresh = 80,
        culprit_sep = ', ',
        stream_policy = 'termination',
        notify_if_no_tty = False,
        notifier = NOTIFIER,
        **kwargs
    ):
        self.errors = 0
        self.version = version
        self.termination_callback = termination_callback
        self.error_status = error_status
        self.flush = flush
        self._stdout = stdout
        self._stderr = stderr
        self.__dict__.update(kwargs)
        self.previous_action = None
        self.logfile = None
        self.logfile_copied = False
        self.length_thresh = length_thresh
        self.culprit_sep = culprit_sep
        if is_str(stream_policy):
            try:
                self.stream_policy = STREAM_POLICIES[stream_policy]
            except KeyError:
                raise Error('unknown stream policy.', culprit=stream_policy)
        else:
            self.stream_policy = stream_policy
        self.notifier = notifier
        self.notify_if_no_tty = notify_if_no_tty
        self.culprit = ()
        self.stream_info = {}

        # make verbosity flags consistent while saving
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
        self.set_logfile(logfile, prev_logfile_suffix)

    # __getattr__ {{{2
    def __getattr__(self, name):
        # returns the attribute value if provided otherwise returns None
        # This is generally used by informants to determine whether an extra
        # value was passed to informer.
        if name.startswith('__'):
            raise AttributeError(name)
        return self.__dict__.get(name)

    # stdout {{{2
    @property
    def stdout(self):
        return self._stdout or sys.stdout

    # stderr {{{2
    @property
    def stderr(self):
        return self._stderr or sys.stderr

    # suppress_output {{{2
    def suppress_output(self, mute=True):
        """Allows you to change the mute flag (only available as a method).

        Args:
            mute (bool):
                If *mute* is True all output is suppressed (it is still logged).
        """
        self.mute = bool(mute)

    # set_logfile {{{2
    def set_logfile(self, logfile, prev_logfile_suffix=None, encoding='utf-8'):
        """Allows you to change the logfile (only available as a method).

        Args:
            logfile:
                May be a pathlib path. May be a string, in which case it is
                taken to be the path of the logfile.  May be *True*, in which
                case ./.<prog_name>.log is used.  May be an open stream.  Or it
                may be *False*, in which case no log file is created.

                Directory containing the logfile must exist.
            prev_logfile_suffix:
                If specified, the existing logfile will be renamed before
                creating the new logfile.  This only occurs the first time the
                logfile is specified.
            encoding (string):
                The encoding to use when writing the file.
        """
        try:
            cached = self.logfile.drain()
        except Exception:
            cached = None
        self.close_logfile()

        if logfile is True:
            logfile = '.%s.log' % self.prog_name if self.prog_name else '.log'

        if prev_logfile_suffix and not self.logfile_copied:
            try:
                prev_logfile = str(logfile) + prev_logfile_suffix
                if os.path.exists(prev_logfile) and os.path.isfile(prev_logfile):
                    os.unlink(prev_logfile)
                if os.path.exists(str(logfile)) and os.path.isfile(str(logfile)):
                    os.rename(str(logfile), prev_logfile)
                    self.logfile_copied = True
            except OSError:
                pass

        try:
            if is_str(logfile):
                logfile = open(logfile, 'w', encoding=encoding)
            elif logfile:  # pathlib
                try:
                    logfile = logfile.open(mode='w', encoding=encoding)
                except AttributeError:
                    pass
            elif logfile:
                assert hasattr(logfile, 'close'), 'expected logfile to be string, path, or stream.'
            # else no logfile
        except OSError as e:
            _print(os_error(e), file=sys.stderr)
            logfile = None

        self.logfile = logfile
        if not logfile:
            return

        # if previous logger was a cache, copy its contents to new logfile
        if cached:
            log(cached, end='')
            return

        # otherwise write header to log file
        if self.prog_name and self.version:
            log('version: %s' % self.version, culprit=self.prog_name)
        now = get_datetime()
        if self.argv is None:
            # self.argv may be None, False or a list. None implies that argv was
            # not available when inform was first loaded (as when loaded from
            # sitecustomize.py). False implies it should not be logged.
            self.argv = sys.argv
        if self.argv:
            log("invoked as: %s" % ' '.join(self.argv), culprit=self.prog_name)
        if now:
            log("log opened on %s." % now, culprit=self.prog_name)

    # flush_logfile {{{2
    def flush_logfile(self):
        "Flush the logfile."
        if self.logfile:
            self.logfile.flush()

    # close_logfile {{{2
    def close_logfile(self, status=None):
        """Close logfile

        If status is given, it is taken to be the exit message or exit status.
        """
        if not self.logfile:
            return
        prog_name = self.prog_name if self.prog_name else sys.argv[0]
        if is_str(status):
            log(status, culprit=prog_name)
        elif status is not None:
            assert 0 <= status < 128
            log('terminates with status {}.'.format(status), culprit=prog_name)
        now = get_datetime()
        log('log closed {}.'.format(now), culprit=prog_name)
        self.logfile.close()
        self.logfile = None

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
            assert action
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
            continuing = options.pop('continuing', False)

            # attach codicils to the message
            codicils = kwargs.get('codicil')
            if codicils:
                codicils = codicils if is_collection(codicils) else [codicils]
                codicils = _join(codicils, dict(sep='\n', wrap=kwargs.get('wrap')))
                if header:
                    codicils = indent(codicils)
                message = message + '\n' + codicils

            messege_color = action.message_color
            header_color = action.header_color
            if action._write_output(self):
                cs = self.colorscheme if Color.isTTY(options['file']) else None
                self._show_msg(
                    # should probably not be passing in the color scheme as it
                    # overrides a scheme explicitly specified in the color
                    # class.  However if I change it it creates numerous errors
                    # in the tests.  I did not have the time to resolve them, so
                    # I am leaving it for now.  This results in an awkward bit
                    # of code in assimilate/overdue.py.
                    header_color(header, scheme=cs) if header else header,
                    header_color(culprit, scheme=cs) if culprit else culprit,
                    messege_color(message, scheme=cs) if message else message,
                    multiline, continuing, options
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
                    multiline, continuing, options
                )

            if action._notify_user(self) or notify_override:
                import subprocess
                urgency = kwargs.get('urgency', 'critical' if action.is_error else None)
                if urgency in ['low', 'normal', 'critical']:
                    urgency = '--urgency=' + urgency
                body = ': '.join(cull([culprit, message]))
                try:
                    subprocess.call(cull([self.notifier, urgency, header, body]))
                except OSError as e:
                    log(os_error(e))
        if action.terminate is not False:
            self.terminate(status=action.terminate)
        self.previous_action = action

    # _get_print_options {{{2
    def _get_print_options(self, kwargs, action):
        opts = dict(
            end = kwargs.get('end', '\n'),
            flush = kwargs.get('flush', self.flush),
            continuing = kwargs.get('continuing', False),
        )
            # sep is handled in _render_message
        if sys.version[0] == '2':  # pragma: no cover
            opts.pop('flush')  # flush is not supported in python2
        if 'file' in kwargs:
            opts['file'] = kwargs['file']
        else:
            opts['file'] = action.stream or self.stream_policy(action, self.stdout, self.stderr)
        return opts

    # _render_message {{{2
    @staticmethod
    def _render_message(args, kwargs):
        return _join(args, kwargs)

    # _render_culprit {{{2
    def _render_culprit(self, kwargs):
        culprit = kwargs.get('culprit')
        if culprit is not None:
            if is_collection(culprit):
                return self.culprit_sep.join(str(c) for c in culprit if c is not None)
            return str(culprit)
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
    def _show_msg(self, header, culprit, message, multiline, continuing, options):
        stream_info = self.get_stream_info(stream=options.get('file'))
        end = options.get('end', '\n')
        terminated = end.endswith('\n')
        if not continuing and not stream_info.empty_line:
            # A continuing message is one where one line of output is built
            # using repeated calls to an informant. An example is the progress
            # bar. This clause is executed if a continuing message is
            # interrupted by a regular message before it has completed, such as
            # when a progress bar is interrupted with an informational message.
            _print(**options)  # start the informational message on a new line
            stream_info.interrupted = True
        if terminated:
            stream_info.empty_line = True
        elif continuing and message:
            stream_info.empty_line = False

        if multiline:
            head = ': '.join(cull([header, culprit]))
            if head:
                _print('%s:\n%s' % (head, indent(message)), **options)
            else:
                _print(indent(message), **options)
        else:
            _print(': '.join(cull([header, culprit, message])), **options)

    # done {{{2
    def done(self, exit=True):
        """Terminate the program with normal exit status.

        Args:
            exit (bool):
                If False, all preparations for termination are done, but
                sys.exit() is not called. Instead, the exit status is returned.

        Returns:
            The desired exit status is returned if exit is False (the function
            does not return if exit is True).
        """
        if self.termination_callback:
            self.termination_callback()
        self.close_logfile('terminates normally.')
        if exit:
            raise SystemExit(0)
        else:
            return 0

    # _compute_exit_status {{{2
    def _compute_exit_status(self, requested_status):
        if requested_status is None:
            return self.error_status if self.errors_accrued() else 0
        if requested_status is True:
            return self.error_status
        if is_str(requested_status):
            log(requested_status)
            _print(requested_status, file=sys.stderr)
            return self.error_status
        return requested_status

    # terminate {{{2
    def terminate(self, status=None, exit=True):
        """Terminate the program with specified exit status.

        Args:
            status (int, bool, string, or None):
                The desired exit status or exit message.
                Exit status is inform.error_status if True is passed in.
                When None, return inform.error_status if errors occurred and 0
                otherwise.  Status may also be a string, in which case it is
                printed to stderr without a header and the exit status is
                inform.error_status.
            exit (bool):
                If False, all preparations for termination are done, but
                sys.exit() is not called. Instead, the exit status is returned.

        Returns:
            The desired exit status is returned if exit is False (the function
            does not return if exit is True).

        Recommended status codes:
            | 0: success
            | 1: unexpected error
            | 2: invalid invocation
            | 3: panic

        Of, if your program naturally want to signal pass or failure using its exit status:
            | 0: success
            | 1: failure
            | 2: error
            | 3: panic
        """
        status = self._compute_exit_status(status)
        if self.termination_callback:
            self.termination_callback()
        self.close_logfile(status)
        if exit:
            raise SystemExit(status)
        else:
            return status

    # terminate_if_errors {{{2
    def terminate_if_errors(self, status=None, exit=True):
        """Terminate the program if error count is nonzero.

        Args:
            status (int, bool or string):
                The desired exit status or exit message.
            exit (bool):
                If False, all preparations for termination are done, but
                sys.exit() is not called. Instead, the exit status is returned.

        Returns:
            None is returned if there is no errors, otherwise the desired exit
            status is returned if exit is False (the function does not return if
            there is an error and exit is True).
        """

        if self.errors:
            return self.terminate(status, exit)
        return None

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

    # get_stream_info {{{2
    def get_stream_info(self, informant=None, stream=None):
        if informant:
            options = self._get_print_options({}, informant)
            stream = options.get('file')

        # get stream name
        aliases = {'<stderr>': '<stdout>'}
            # treat stdout and stderr as the same stream
            # they are usually sent to the tty
        try:
            name = aliases.get(stream.name, stream.name)
        except AttributeError:
            name = id(stream)

        # get stream info
        info = self.stream_info.get(name)
        if not info:
            info = Info(name=name, empty_line=True, stream=stream)
        self.stream_info[name] = info
        return info


    # __enter__ {{{2
    def __enter__(self):
        return self

    # __exit__ {{{2
    def __exit__(self, type, value, traceback):
        self.disconnect()

    # culprit {{{2
    # first create a context manager
    class CulpritContextManager:
        def __init__(self, informer, culprit, append=True):
            self.informer = informer
            if culprit is None:
                self.culprit = ()
            else:
                self.culprit = tuple(culprit) if is_collection(culprit) else (culprit,)
            self.append = append

        def __enter__(self):
            self.saved_culprit = self.informer.culprit
            if self.append:
                self.informer.culprit += self.culprit
            else:
                self.informer.culprit = self.culprit

        def __exit__(self, *args):
            self.informer.culprit = self.saved_culprit

    # set/replace the culprit
    def set_culprit(self, culprit):
        """Set the culprit while temporarily displacing current culprit.

        Squirrels away a culprit for later use. Any existing culprit is moved
        out of the way.

        Args:
            culprit (string, number or tuple of strings and numbers):
                A culprit or collection of culprits that are cached with the
                intent that they be available to be included in a message upon
                demand. They generally are used to indicate what a message
                refers to.

        This function is designed to work as a context manager, meaning that it
        meant to be used with Python's *with* statement. It temporarily replaces
        any existing saved culprit, but that culprit in reinstated upon exiting the
        *with* statement. Once a culprit is saved, :meth:`inform.Inform.get_culprit`
        is used to access it.

        **Example**::

            >>> from inform import get_culprit, set_culprit, warn

            >>> def count_lines(lines):
            ...    empty = 0
            ...    for lineno, line in enumerate(lines):
            ...        if not line:
            ...            warn('empty line.', culprit=get_culprit(lineno+1))

            >>> filename = 'pyproject.toml'
            >>> with open(filename) as f, set_culprit(filename):
            ...    lines = f.read().splitlines()
            ...    num_lines = count_lines(lines)
            warning: pyproject.toml, 25: empty line.
            warning: pyproject.toml, 37: empty line.
            warning: pyproject.toml, 43: empty line.

        """
        return self.CulpritContextManager(self, culprit, append=False)

    # add to the culprit
    def add_culprit(self, culprit):
        """Add to the currently saved culprit.

        Similar to :meth:`Inform.set_culprit` except that this method appends
        the given culprit to the cached culprit rather than simply replacing it.

        Args:
            culprit (string, number or tuple of strings and numbers):
                A culprit or collection of culprits that are cached with the
                intent that they be available to be included in a message upon
                demand. They generally are used to indicate what a message
                refers to.

        This function is designed to work as a context manager, meaning that it
        meant to be used with Python's *with* statement. It temporarily replaces
        any existing culprit, but that culprit in reinstated upon exiting the
        *with* statement. Once a culprit is saved, :meth:`inform.Inform.get_culprit`
        is used to access it.

        See :meth:`Inform.set_culprit` for an example of a closely related
        method.
        """
        return self.CulpritContextManager(self, culprit, append=True)

    # get the culprit
    def get_culprit(self, culprit=None):
        """Get the current culprit.

        Return the currently cached culprit as a tuple. If a culprit is specified as an
        argument, it is appended to the cached culprit without modifying it.

        Args:
            culprit (string, number or tuple of strings and numbers):
                A culprit or collection of culprits that is appended to the
                return value without modifying the cached culprit.

        Returns:
            The culprit argument is appended to the cached culprit and the
            combination is returned. The return value is always in the form of a
            tuple even if there is only one component.

        See :meth:`Inform.set_culprit` for an example use of this method.
        """
        if culprit is not None:
            culprit = tuple(culprit) if is_collection(culprit) else (culprit,)
            return self.culprit + culprit
        return self.culprit

    # join culprit
    def join_culprit(self, culprit):
        """Join the specified culprits with the current culprit separators.

        Culprits are returned from the informer or for exceptions as a tuple.
        This function allows you to join those culprits into a string.

        Args:
            culprit (tuple of strings or numbers)

        Returns:
            The culprit tuple joined into a string.
        """
        return self.culprit_sep.join(str(c) for c in culprit)


# Direct access to class methods {{{1
# done {{{2
def done(exit=True):
    """Terminate the program with normal exit status.

    Calls :meth:`inform.Inform.done` for the active informer.
    """
    return INFORMER.done(exit)


# terminate {{{2
def terminate(status=None, exit=True):
    """Terminate the program with specified exit status."

    Calls :meth:`inform.Inform.terminate` for the active informer.
    """
    return INFORMER.terminate(status, exit)


# terminate_if_errors {{{2
def terminate_if_errors(status=None, exit=True):
    """Terminate the program if error count is nonzero."

    Calls :meth:`inform.Inform.terminate_if_errors` for the active informer.
    """
    return INFORMER.terminate_if_errors(status, exit)


# errors_accrued {{{2
def errors_accrued(reset=False):
    """Returns number of errors that have accrued."

    Calls :meth:`inform.Inform.errors_accrued` for the active informer.
    """
    return INFORMER.errors_accrued(reset)


# get_prog_name {{{2
def get_prog_name():
    """Returns the program name.

    Calls :meth:`inform.Inform.get_prog_name` for the active informer.
    """
    return INFORMER.get_prog_name()


# get_informer {{{2
def get_informer():
    """Returns the active informer."""
    return INFORMER


# set_informer {{{2
def set_informer(new):
    """Replaces the existing informer and returns the old one."""
    global INFORMER
    old = INFORMER
    INFORMER = new
    return old


# set/replace the culprit {{{2
def set_culprit(culprit):
    """Set the culprit while displacing current culprit.

    Calls :meth:`inform.Inform.set_culprit` for the active informer.
    """
    return INFORMER.set_culprit(culprit)

# add to the culprit {{{2
def add_culprit(culprit):
    """Append to the end of the current culprit.

    Calls :meth:`inform.Inform.add_culprit` for the active informer.
    """
    return INFORMER.add_culprit(culprit)

# get the culprit {{{2
def get_culprit(culprit=None):
    """Get the current culprit.

    Calls :meth:`inform.Inform.get_culprit` for the active informer.
    """
    return INFORMER.get_culprit(culprit)


# join culprit {{{2
def join_culprit(culprit=None):
    """Join the given culprit tuple into a string.

    Calls :meth:`inform.Inform.join_culprit` for the active informer.
    """
    return INFORMER.join_culprit(culprit)


# Instantiate default informer {{{1
DEFAULT_INFORMER = Inform()
INFORMER = DEFAULT_INFORMER


# Exceptions {{{1
# Error {{{2
class Error(Exception):
    """A generic exception.

    The exception accepts both unnamed and named arguments.
    All are recorded and available for later use.

    *template* may be added to the class as an attribute, in which case it acts
    as the default template for the exception (used to format the exception
    arguments into an error message).

    The idea of allowing *template* to be an attribute to *Error* was originally
    proposed on the Python Ideas mailing list by Ryan Fox
    (https://pypi.org/project/exception-template/).
    """

    # constructor {{{3
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # convert culprit, codicil to tuples while removing any Nones
        for attr in ['culprit', 'codicil']:
            if attr in kwargs:
                value = kwargs.get(attr)
                if not is_collection(value):
                    value = (value,)
                value = cull(value, remove=None)
                if value:
                    self.kwargs[attr] = value
                else:
                    del self.kwargs[attr]

        # use template attribute from class if template is not give as argument
        if 'template' not in kwargs:
            template = getattr(self, 'template', None)
            if template:
                self.kwargs.update(dict(template=template))

    # get_message {{{3
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

        Returns:
            The formatted message without the culprits.
        """
        if not template:
            template = getattr(self, 'template', None)
        if template:
            kwargs = self.kwargs.copy()
            kwargs.update(dict(template=template))
        else:
            kwargs = self.kwargs
        return _join(self.args, kwargs)

    # get_culprit {{{3
    def get_culprit(self, culprit=None):
        """Get the culprits.

        Culprits are extra pieces of information attached
        to an error that help to identify the source of the error. For example,
        file name and line number where the error was found are often attached
        as culprits.

        Return the culprit as a tuple. If a culprit is specified as an
        argument, it is appended to the exception's culprit without modifying it.

        Args:
            culprit (string, number or tuple of strings and numbers):
                A culprit or collection of culprits that is appended to the
                return value without modifying the cached culprit.

        Returns:
            The culprit argument is prepended to the exception's culprit and the
            combination is returned. The return value is always in the form of a
            tuple even if there is only one component.
        """
        exception_culprit = self.kwargs.get('culprit', ())
        if not is_collection(exception_culprit):
            exception_culprit = (exception_culprit,)
        if culprit is not None:
            if not is_collection(culprit):
                culprit = (culprit,)
            return culprit + exception_culprit
        return exception_culprit

    # get_codicil {{{3
    def get_codicil(self, codicil=None):
        """Get the codicils.

        A codicil is extra text attached to an error that can clarify the error
        message or to give extra context.

        Return the codicil as a tuple. If a codicil is specified as an
        argument, it is appended to the exception's codicil without modifying it.

        Args:
            codicil (string or tuple of strings):
                A codicil or collection of codicils that is appended to the
                return value without modifying the cached codicil.

        Returns:
            The codicil argument is appended to the exception's codicil and the
            combination is returned. The return value is always in the form of a
            tuple even if there is only one component.
        """
        exception_codicil = self.kwargs.get('codicil', getattr(self, 'codicil', ()))
        if exception_codicil and not is_collection(exception_codicil):
            exception_codicil = (exception_codicil,)
        if codicil:
            if not is_collection(codicil):
                codicil = (codicil,)
            return exception_codicil + codicil
        return exception_codicil

    # report {{{3
    def report(self, **new_kwargs):
        """Report exception to the user.

        Prints the error message on the standard output.

        The :func:`inform.error` function is called with the exception arguments.

        Args:
            \\**kwargs:
                *report()* takes any of the normal keyword arguments normally
                allowed on an informant (culprit, template, etc.). Any keyword
                argument specified here overrides those that were specified when
                the exception was first raised.
        """
        if new_kwargs:
            kwargs = self.kwargs.copy()
            kwargs.update(new_kwargs)
        else:
            kwargs = self.kwargs
        informant = kwargs.get('informant', error)
        informant(*self.args, **kwargs)

    # terminate {{{3
    def terminate(self, **new_kwargs):
        """Report exception and terminate.

        Prints the error message on the standard output and exits the program.

        The :func:`inform.fatal` function is called with the exception arguments.

        Args:
            \\**kwargs:
                *report()* takes any of the normal keyword arguments normally
                allowed on an informant (culprit, template, etc.). Any keyword
                argument specified here overrides those that were specified when
                the exception was first raised.
        """
        if new_kwargs:
            kwargs = self.kwargs.copy()
            kwargs.update(new_kwargs)
        else:
            kwargs = self.kwargs
        fatal(*self.args, **kwargs)

    # reraise {{{3
    def reraise(self, **new_kwargs):
        "Re-raise the exception with replaced arguments."
        self.kwargs.update(new_kwargs)
        raise

    # render {{{3
    def render(self, template=None, include_codicil=True):
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

            include_codicil (bool):
                Include the codicil in the rendered message.

        Returns:
            The formatted message with any culprits.
        """
        message = self.get_message(template)
        culprit = join_culprit(self.get_culprit())
        message = f"{culprit}: {message}" if culprit else message
        if include_codicil:
            codicil = self.get_codicil()
            if codicil:
                # codicil = '\n\n'.join(cull(codicil))
                codicil = '\n'.join(codicil)
                return f"{message}\n{indent(codicil)}"
        return message

    def __str__(self):
        return self.render()

    def __getattr__(self, name):
        # returns the value associated with name in kwargs if it exists,
        # otherwise None
        if name.startswith('__'):
            raise AttributeError(name)
        return self.kwargs.get(name)
