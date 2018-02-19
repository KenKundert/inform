.. Initialize Inform and suppress outputting of program name

    >>> from inform import Inform, error
    >>> inform = Inform(prog_name=False)
    >>> fatal = error


Inform: Print & Logging Utilities
=================================

| Version: 1.12.0
| Released: 2018-02-18
| Please post all bugs and suggestions at
  `Github <https://github.com/KenKundert/inform/issues>`_
  (or contact me directly at
  `inform@nurdletech.com <mailto://inform@nurdletech.com>`_).


*Inform* is designed to display messages from programs that are typically run 
from a console.  It provides a collection of 'print' functions that allow you to 
simply and cleanly print different types of messages.  For example:

.. code-block:: python

    >>> from inform import display, warn, error
    >>> display('This is a plain message.')
    This is a plain message.

    >>> error('this is an error message.')
    error: this is an error message.

These functions behave in a way that is very similar to the *print* function 
that is built-in to Python3, but they also provide some additional features as 
well. For example, they can be configured to log their messages and they can be 
disabled en masse.

Finally, *Inform* provides a generic exception and a collection of small 
utilities that are useful when creating messages.


Alternatives
------------

The Python standard library provides the `logging 
<https://docs.python.org/3/library/logging.html>`_ package.  This package 
differs from *Inform* in that it is really intended to log events to a file. It 
is more intended for daemons that run in the background and the logging is not 
meant to communicate directly to the user in real time, but rather record enough 
information into a log file for an administrator to understand how well the 
program is performing and whether anything unusual is happening.

In contrast, *Inform* is meant to used to provide information from command line 
utilities directly to the user in real time. It is not confined to only logging 
events, but instead can be used anywhere the normal Python *print* function 
would be used. In effect, *Inform* allows you to create and use multiple print 
functions each of which is tailored for a specific situation or task. This of 
course is something you could do yourself using the built-in *print* function, 
but with *Inform* you will not have to embed your print functions in complex 
condition statements, every message is formatted in a consistent manner that 
follows normal Unix conventions, and you can control all of your print functions 
by configuring a single object.


Installation
------------

Install with::

   pip3 install --user inform

Requires Python2.7 or Python3.3 or better.


Quick Tour
----------

Informants
""""""""""

*Inform* defines a collection of *print*-like functions that have different 
roles.  These functions are referred to as 'informants' and include 
:ref:`display`, :ref:`warn`, :ref:`error`, and :ref:`fatal`.  All of them take 
arguments in the same manner as Python's built-in print function and all of them 
write the desired message to standard output, with the last three adding 
a header to the message that indicates the type of message.  For example:

.. code-block:: python

    >>> display('ice', 9)
    ice 9

    >>> warn('cannot write to file, logging suppressed.')
    warning: cannot write to file, logging suppressed.

    >>> filename = 'config'
    >>> error('%s: file not found.' % filename)
    error: config: file not found.

    >>> fatal('defective input file.', culprit=filename)
    error: config: defective input file.

Notice that in the error message the filename was explicitly added to the front 
of the message. This is an extremely common idiom and it is provided by *Inform* 
using the *culprit* named argument as shown in the fatal message.
*fatal* is similar to *error* but additionally terminates the program.  To make 
the error messages stand out, the header is generally rendered in a color 
appropriate to the message, so warnings use yellow and errors use red.  However, 
they are not colored above because messages are only colored if they are being 
written to the console (a TTY).

In a manner similar to Python3's built-in *print* function, unnamed arguments 
are converted to strings and then joined using the separator, which by default 
is a single space but can be specified using the *sep* named argument.

.. code-block:: python

    >>> colors = dict(red='ff5733', green='4fff33', blue='3346ff')

    >>> lines = []
    >>> for key in sorted(colors.keys()):
    ...     val = colors[key]
    ...     lines.append('{key:>5s} = {val}'.format(key=key, val=val))

    >>> display(*lines, sep='\n')
     blue = 3346ff
    green = 4fff33
      red = ff5733

Alternatively, you can specify an arbitrary collection of named and unnamed 
arguments, and form them into a message using the *template* argument:

.. code-block:: python

    >>> for key in sorted(colors.keys()):
    ...     val = colors[key]
    ...     display(val, k=key, template='{k:>5s} = {}')
     blue = 3346ff
    green = 4fff33
      red = ff5733

You can even specify a collection of templates.  The first one for which all 
keys are known is used.  For example;

.. code-block:: python

    >>> colors = dict(
    ...     red = ('ff5733', 'failure'),
    ...     green = ('4fff33', 'success'),
    ...     blue = ('3346ff', None),
    ... )

    >>> for name in sorted(colors.keys()):
    ...     code, desc = colors[name]
    ...     templates = ('{:>5s} = {}  -- {}', '{:>5s} = {}')
    ...     display(name, code, desc, template=templates)
     blue = 3346ff
    green = 4fff33  -- success
      red = ff5733  -- failure

    >>> for name in sorted(colors.keys()):
    ...     code, desc = colors[name]
    ...     templates = ('{k:>5s} = {v}  -- {d}', '{k:>5s} = {v}')
    ...     display(k=name, v=code, d=desc, template=templates)
     blue = 3346ff
    green = 4fff33  -- success
      red = ff5733  -- failure

All informants support the *culprit* named argument, which is used to identify 
the object of the message.  The *culprit* can be a scalar, as above, or 
a collection, in which case the members of the collection are joined 
together:

.. code-block:: python

    >>> line = 5
    >>> display('syntax error.', culprit=(filename, line))
    config, 5: syntax error.

Besides the four informants already described, *Inform* provides several others, 
including :ref:`log`, :ref:`codicil`, :ref:`comment`, :ref:`narrate`, 
:ref:`output`, :ref:`notify`, :ref:`debug` and :ref:`panic`.  Informants in 
general can write to the log file, to the standard output, or to a notifier.  
They can add headers and specify the color of the header and the message. They 
can also continue the previous message or they can terminate the program.  Each 
informant embodies a predefined set of these choices. In addition, they are 
affected by options passed to the active informer (described next), which is 
often used to enable or disable informants based on various verbosity options.


Controlling Informants
""""""""""""""""""""""

For more control of the informants, you can import and instantiate the 
:class:`inform.Inform` class yourself along with the desired informants.  This 
gives you the ability to specify options:

.. code-block:: python

    >>> from inform import Inform, display, error
    >>> Inform(logfile=True, prog_name="teneya", quiet=True)
    <...>
    >>> display('Initializing ...')

    >>> error('file not found.', culprit='data.in')
    teneya error: data.in: file not found.

Notice that in this case the call to *display* did not print anything. That is 
because the *quiet* argument was passed to *Inform*, which acts to suppress all 
but error messages. However, a logfile was specified, so the message would be 
logged. In addition, the program name was specified, with the result in it being 
added to the header of the error message.

An object of the *Inform* class is referred to as an informer (not to be 
confused with the print functions, which are  referred to as informants). Once 
instantiated, you can use the informer to change various settings, terminate the 
program, or return a count of the number of errors that have occurred.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name=False)
    >>> error('file not found.', culprit='data.in')
    error: data.in: file not found.
    >>> informer.errors_accrued()
    1


Utility Functions
"""""""""""""""""

*Inform* provides a collection of utility functions that are often useful when 
constructing messages.

.. list-table::

   * - :ref:`color desc`
     - Used to color messages sent to the console.

   * - :ref:`columns desc`
     - Distribute an array over enough columns to fill the screen.

   * - :ref:`conjoin desc`
     - Like join, but adds a conjunction between the last two items.

   * - :ref:`cull desc`
     - Strips uninteresting value from collections.

   * - :ref:`ddd desc`
     - Pretty prints its arguments, used when debugging code.

   * - :ref:`fmt desc`
     - Similar to format(), but can pull arguments from the local scope.

   * - :ref:`full_stop desc`
     - Add a period to end of string if it has no other punctuation.

   * - :ref:`indent desc`
     - Adds indentation.

   * - :ref:`is_collection desc`
     - Is object a collection (i.e., is it iterable and not a string)?

   * - :ref:`is_iterable desc`
     - Is object iterable (includes strings).

   * - :ref:`is_str desc`
     - Is object a string?

   * - :ref:`join desc`
     - Combines arguments into a string in the same way as informant.

   * - :ref:`os_error desc`
     - Generates clean messages for operating system errors

   * - :ref:`plural desc`
     - Pluralizes a word if needed.

   * - :ref:`ppp desc`
     - Print function, used when debugging code.

   * - :ref:`render desc`
     - Converts many of the built-in Python data types into attractive, compact, 
       and easy to read strings.

   * - :ref:`sss desc`
     - Prints stack trace, used when debugging code.

   * - :ref:`vvv desc`
     - Print all variables that have given value, used when debugging code.

One of the most used is *os_error*.  It converts *OSError* exceptions into 
a simple well formatted string that can be used to describe the exception to the 
user.

.. code-block:: python

    >>> from inform import os_error, error
    >>> try:
    ...     with open(filename) as f:
    ...         config = f.read()
    ... except (OSError, IOError) as e:
    ...     error(os_error(e))
    error: config: no such file or directory.


Generic Exception
"""""""""""""""""

*Inform* also provides a generic exception, :class:`inform.Error`, that can be 
used directly or can be subclassed to create your own exceptions.  It takes 
arguments in the same manner as informants, and provides some useful methods 
used when reporting errors:

.. code-block:: python

    >>> from inform import Error

    >>> def read_config(filename):
    ...     try:
    ...         with open(filename) as f:
    ...             config = f.read()
    ...     except (OSError, IOError) as e:
    ...         raise Error(os_error(e))

    >>> try:
    ...     read_config('config')
    ... except Error as e:
    ...     e.report()
    error: config: no such file or directory.


Documentation
-------------

.. toctree::
   :maxdepth: 1

   user
   api
   releases
