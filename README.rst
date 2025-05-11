Inform — Print & Logging Utilities
==================================

|downloads| |build status| |coverage| |rtd status| |pypi version| |anaconda version| |python version|

:Author: Ken Kundert
:Version: 1.34
:Released: 2025-05-10

A package that provides specialized print functions that are used when 
communicating with the user. It allows you to easily print attractive, 
informative, and consistent error messages.  For example:

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

    pip3 install inform

You can find the latest development version of the source code on
`Github <https://github.com/KenKundert/inform>`_.


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

    >>> from inform import Error, did_you_mean

    >>> known_names = 'alpha beta gamma delta epsilon'.split()
    >>> name = 'alfa'

    >>> try:
    ...     if name not in known_names:
    ...         raise Error(name, template="name '{}' is not defined.")
    ... except Error as e:
    ...     candidates = did_you_mean(e.args[0], known_names)
    ...     e.report(codicil = f"Did you mean {candidates}?")
    myprog error: name 'alfa' is not defined.
        Did you mean alpha?


Utilities
---------

Several utility functions and classes are provided for your convenience. They 
are often helpful when creating messages.

dedent:
    Dedents a block of text.

indent:
    Indents a block of text.

conjoin:
    Like ''.join(), but allows you to specify a conjunction that is placed 
    between the last two elements, ex:

    .. code-block:: python

        >>> from inform import conjoin
        >>> conjoin(['a', 'b', 'c'])
        'a, b and c'

        >>> conjoin(['a', 'b', 'c'], conj=' or ')
        'a, b or c'

did_you_mean:
    Given a word and list of candidates, returns the candidate that is most 
    similar to the word.

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

truth:
    Like plural, but for Booleans.

full_stop:
    Adds a period to the end of the string if needed (if the last character is 
    not a period, question mark or exclamation mark).

title_case:
    Converts the initial letters in the words of a string to upper case while 
    maintaining any letters that are already upper case, such as acronyms.

format_range, parse_range:
    Converts a set of numbers to and from a succinct, readable string that 
    summarizes the set.  For example:

    .. code-block:: python

        >>> from inform import format_range, parse_range

        >>> format_range({1, 2, 3, 5})
        '1-3,5'

        >>> parse_range('1-3,5')
        {1, 2, 3, 5}

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

Color:
    A class is used to add color to text.

Info:
    A utility class that automatically converts all keyword arguments into 
    attributes.

ProgessBar:
    A class that produces an interruptable progress bar.

render_bar:
    Converts generates a text bar whose width is controlled by a normalized 
    value.


.. |build status| image:: https://github.com/KenKundert/inform/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/KenKundert/inform/actions/workflows/build.yaml

.. |downloads| image:: https://pepy.tech/badge/inform/month
    :target: https://pepy.tech/project/inform

.. |rtd status| image:: https://img.shields.io/readthedocs/inform.svg
   :target: https://inform.readthedocs.io/en/latest/?badge=latest

.. |coverage| image:: https://img.shields.io/coveralls/KenKundert/inform.svg
    :target: https://coveralls.io/r/KenKundert/inform

.. |pypi version| image:: https://img.shields.io/pypi/v/inform.svg
    :target: https://pypi.python.org/pypi/inform

.. |anaconda version| image:: https://anaconda.org/conda-forge/inform/badges/version.svg
    :target: https://anaconda.org/conda-forge/inform

.. |python version| image:: https://img.shields.io/pypi/pyversions/inform.svg
    :target: https://pypi.python.org/pypi/inform/


