Inform - Print & Logging Utilities
==================================

.. image:: https://img.shields.io/travis/KenKundert/inform/master.svg
    :target: https://travis-ci.org/KenKundert/inform

.. image:: https://img.shields.io/coveralls/KenKundert/inform.svg
    :target: https://coveralls.io/r/KenKundert/inform

.. image:: https://img.shields.io/pypi/v/inform.svg
    :target: https://pypi.python.org/pypi/inform

.. image:: https://img.shields.io/pypi/pyversions/inform.svg
    :target: https://pypi.python.org/pypi/inform/


:Author: Ken Kundert
:Version: 1.25.0
:Released: 2021-07-07

A light-weight package with few dependencies that provides specialized print 
functions that are used when communicating with the user. It allows you to 
easily print attractive, informative, and consistent error messages.  For 
example:

.. code-block:: python

    >> from inform import display, warn, error
    >> display(
    ..     'Display is like print'
    ..     'except that it supports logging and can be disabled.'
    ..     sep=', ')
    Display is like print, except that it supports logging and can be disabled.

    >> warn('warnings get a header that is printed in yellow.')
    warning: warnings get a header that is printed in yellow.

    >> error('errors get a header that is printed in red.')
    error: errors get a header that is printed in red.

Inform also provides logging and output control.

In addition, Inform provides a powerful generic exception that can be used 
directly as a general purpose exception, or can be subclassed to produce 
powerful specialized exceptions.  Inform exceptions are unique in that they keep 
all of the named and unnamed arguments so they can be used when reporting 
errors.

You can find the documentation on `ReadTheDocs
<https://inform.readthedocs.io>`_. You can download and install the latest
stable version of the code from `PyPI <https://pypi.python.org>`_ using::

    pip3 install --user --upgrade inform

You can find the latest development version of the source code on
`Github <https://github.com/KenKundert/inform>`_.

Supported in Python2.7, Python3.5, Python3.6, Python3.7 and Python3.8.


Introduction
------------

This package defines a collection of *print* functions that have different 
roles.  These functions are referred to as *informants* and are described below 
in the Informants section. They include include *log*, *comment*, *codicil*, 
*narrate*, *display*, *output*, *notify*, *debug*, *warn*, *error*, *fatal* and 
*panic*.

With the simplest use of the program, you simply import the informants you need 
and call them (they take the same arguments as Python's built-in *print* 
function):

.. code-block:: python

    >>> from inform import display
    >>> display('ice', 9)
    ice 9

For more control of the informants, you can import and instantiate the Inform 
class yourself along with the desired informants.  This gives you the ability to 
specify options:

.. code-block:: python

    >>> from inform import Inform, display, error
    >>> Inform(logfile=False, prog_name=False)
    <...>
    >>> display('hello')
    hello
    >>> error('file not found.', culprit='data.in')
    error: data.in: file not found.

An object of the Inform class is referred to as an informer (not to be confused 
with the print functions, which are  referred to as informants). Once 
instantiated, you can use the informer to change various settings, terminate the 
program, or return a count of the number of errors that have occurred.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="prog")
    >>> error('file not found.', culprit='data.in')
    prog error: data.in: file not found.
    >>> informer.errors_accrued()
    1

You can create your own informants:

.. code-block:: python

    >>> from inform import Inform, InformantFactory

    >>> verbose1 = InformantFactory(output=lambda m: m.verbosity >= 1)
    >>> verbose2 = InformantFactory(output=lambda m: m.verbosity >= 2)
    >>> with Inform(verbosity=0):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')

    >>> with Inform(verbosity=1):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')
    First level of verbosity.

    >>> with Inform(verbosity=2):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')
    First level of verbosity.
    Second level of verbosity.

The argument *verbosity* is not an explicitly supported argument to Inform.  In 
this case Inform simply saves the value and makes it available as an attribute, 
and it is this attribute that is queried by the lambda function passed to the 
InformantFactory when creating the informants.


Exception
---------
An exception, *Error*, is provided that takes the same arguments as an 
informant.  This allows you to catch the exception and handle it if you like.  
The exception provides the *report* and *terminate* methods that processes the 
exception as an error or fatal error if you find that you can do nothing else 
with the exception:

.. code-block:: python

    >>> from inform import Inform, Error

    >>> Inform(prog_name='myprog')
    <...>
    >>> try:
    ...     raise Error('must not be zero.', culprit='naught')
    ... except Error as e:
    ...     e.report()
    myprog error: naught: must not be zero.

*Error* also provides get_message() and get_culprit() methods, which return the 
message and the culprit. You can also cast the exception to a string to get 
a string that contains both the message and the culprit formatted so that it can 
be shown to the user.

Any keyword arguments provided will be available in *e.kwargs*, but certain 
keyword arguments are reserved by inform (see above).

One common approach to using *Error* is to pass all the arguments that make up 
the error message as unnamed arguments and then assemble them into the message 
by providing a template.  In that way the arguments are directly available to 
the handler if needed. For example:

.. code-block:: python

    >>> from difflib import get_close_matches
    >>> from inform import Error, codicil, conjoin, fmt

    >>> known_names = 'alpha beta gamma delta epsilon'.split()
    >>> name = 'alfa'

    >>> try:
    ...     if name not in known_names:
    ...         raise Error(name, template="name '{}' is not defined.")
    ... except Error as e:
    ...     candidates = get_close_matches(e.args[0], known_names, 1, 0.6)
    ...     candidates = conjoin(candidates, conj=' or ')
    ...     e.report()
    ...     codicil(fmt('Did you mean {candidates}?'))
    myprog error: name 'alfa' is not defined.
        Did you mean alpha?


Utilities
---------

Several utility functions are provided for your convenience. They are often 
helpful when creating messages.

indent:
    Indents the text.

conjoin:
    Like ''.join(), but allows you to specify a conjunction that is placed 
    between the last two elements, ex:

    .. code-block:: python

        >>> from inform import conjoin
        >>> conjoin(['a', 'b', 'c'])
        'a, b and c'

        >>> conjoin(['a', 'b', 'c'], conj=' or ')
        'a, b or c'

cull:
    Strips items from a collection that have a particular value.

join:
    Combines the arguments in a manner very similar to an informant and returns 
    the result as a string.

fmt:
    Similar to ''.format(), but it can pull arguments from the local scope.

render:
    Recursively convert an object to a string with reasonable formatting.  Has 
    built in support for the base Python types (None, bool, int, float, str, 
    set, tuple, list, and dict).  If you confine yourself to these types, the 
    output of render() can be read by the Python interpreter. Other types are 
    converted to string with repr().

plural:
    Produces either the singular or plural form of a word based on a count.

full_stop:
    Adds a period to the end of the string if needed (if the last character is 
    not a period, question mark or exclamation mark).

columns:
    Distribute array over enough columns to fill the screen.

os_error:
    Generates clean messages for operating system errors.

is_str:
    Returns *True* if its argument is a string-like object.

is_iterable:
    Returns *True* if its argument is iterable.

is_collection:
    Returns *True* if its argument is iterable but is not a string.

is_mapping:
    Returns *True* if its argument is a mapping (are dictionary like).

For example:

.. code-block:: python

    >>> from inform import Inform, display, error, conjoin, cull, fmt, os_error

    >>> Inform(prog_name=False)
    <...>
    >>> filenames = cull(['a', 'b', None, 'd'])
    >>> filetype = 'CSV'
    >>> display(
    ...     fmt(
    ...         'Reading {filetype} files: {names}.',
    ...         names=conjoin(filenames),
    ...     )
    ... )
    Reading CSV files: a, b and d.

    >>> contents = {}
    >>> for name in filenames:
    ...     try:
    ...         with open(name) as f:
    ...             contents[name] = f.read()
    ...     except IOError as e:
    ...         error(os_error(e))
    error: a: no such file or directory.
    error: b: no such file or directory.
    error: d: no such file or directory.

Notice that *filetype* was not explicitly passed into *fmt()* even though it was 
explicitly called out in the format string.  *filetype* can be left out of the 
argument list because if *fmt* does not find a named argument in its argument 
list, it will look for a variable of the same name in the local scope.

Here is an example of render():

.. code-block:: python

    >>> from inform import render, display
    >>> s1='alpha string'
    >>> s2='beta string'
    >>> n=42
    >>> S={s1, s2}
    >>> L=[s1, n, S]
    >>> d = {1:s1, 2:s2}
    >>> D={'s': s1, 'n': n, 'S': S, 'L': L, 'd':d}
    >>> display('D', '=', render(D, True))
    D = {
        'L': [
            'alpha string',
            42,
            {'alpha string', 'beta string'},
        ],
        'S': {'alpha string', 'beta string'},
        'd': {1: 'alpha string', 2: 'beta string'},
        'n': 42,
        's': 'alpha string',
    }

Finally, here is an example of full_stop and columns. It prints out the phonetic 
alphabet.

.. code-block:: python

    >>> from inform import columns, full_stop
    >>> title = 'Display the NATO phonetic alphabet'
    >>> words = """
    ...     Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett Kilo
    ...     Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform
    ...     Victor Whiskey X-ray Yankee Zulu
    ... """.split()
    >>> display(full_stop(title), columns(words), sep='\n')
    Display the NATO phonetic alphabet.
        Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
        Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
        Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
        Delta     Hotel     Lima      Papa      Tango     X-ray

Debugging Functions
"""""""""""""""""""
The debugging functions are intended to be used when you want to print something 
out when debugging your program.  They are colorful to make it easier to find 
them among the program's normal output, and a header is added that describes 
the location they were called from. This makes it easier to distinguish several 
debug message and also makes it easy to find and remove the functions once you 
are done debugging.

ppp:
    This function is very similar to the normal Python print function.

    .. code:: python

        >>> from inform import ppp, ddd, sss, vvv
        >>> a = 1
        >>> b = 'this is a test'
        >>> c = (2, 3)
        >>> d = {'a': a, 'b': b, 'c': c}
        >>> ppp(a, b, c)
        DEBUG: <doctest README.rst[52]>, 1, __main__: 1 this is a test (2, 3)

ddd:
    This function is pretty prints all of both the unnamed and named arguments.

    .. code:: python

        >>> ddd(a, b, c=c, d=d)
        DEBUG: <doctest README.rst[53]>, 1, __main__:
            1
            'this is a test'
            c = (2, 3)
            d = {
                'a': 1,
                'b': 'this is a test',
                'c': (2, 3),
            }

    If you give named arguments, the name is prepended to its value.


vvv:
    This function prints variables from the calling scope. If no arguments are 
    given, then all the variables are printed. You can optionally give specific 
    variables on the argument list and only those variables are printed.

    .. code:: python

        >>> vvv(b, d)
        DEBUG: <doctest README.rst[54]>, 1, __main__:
            b = 'this is a test'
            d = {
                'a': 1,
                'b': 'this is a test',
                'c': (2, 3),
            }


sss:
    This function prints a stack trace, which can answer the *How did I get 
    here?* question better than a simple print function.

    .. code:: python

        >> def foo():
        ..     sss()
        ..     print('CONTINUING')

        >> foo()
        DEBUG: <doctest README.rst[93]>:2, __main__.foo():
            Traceback (most recent call last):
                ...
        CONTINUING


Color Class
"""""""""""

The Color class creates colorizers, which are used to render text in 
a particular color.  They are like the Python print function in that they take 
any number of unnamed arguments that are converted to strings and then joined 
into a single string. The string is then coded for the chosen color and 
returned. For example:

.. code-block:: python

   >> from inform import Color, display

   >> green = Color('green')
   >> red = Color('red')
   >> success = green('pass:')
   >> failure = red('FAIL:')

   >> failures = {'outrigger': True, 'signalman': False}
   >> for name, fails in failures.items():
   ..     result = failure if fails else success
   ..     display(result, name)
   FAIL: outrigger
   pass: signalman

When the messages print, the 'pass:' will be green and 'FAIL:' will be red.
