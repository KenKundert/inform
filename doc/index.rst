Inform: Print & Logging Utilities
=================================

| Version: 1.10.2
| Released: 2017-12-04
| Please post all bugs and suggestions at
  `Github <https://github.com/KenKundert/inform/issues>`_
  (or contact me directly at
  `inform@nurdletech.com <mailto://inform@nurdletech.com>`_).


A light-weight package with few dependencies that provides various print-like 
functions that are used in command-line programs when communicating with the 
user.  It allows you to easily print attractive, informative, and consistent 
user messages.  For example:

.. code-block:: python

    >> from inform import display, warn, error, fatal
    >> display('This is a plain message.')
    This is a plain message.

    >> warn('this is a warning message.')
    warning: this is a warning message.

    >> error('this is an error message.')
    error: this is an error message.

    >> fatal('this is a fatal error message.')
    error: this is a fatal error message.


Inform also provides logging, output control, a generic exception, and various 
utilities that are useful when creating messages.

Alternative
-----------

The Python standard library provides the `logging 
<https://docs.python.org/3/library/logging.html>`_ package.  This package 
differs from *Inform* in that it is really intended to log events to a file. It 
is more intended for daemons that run in the background and the logging is not 
meant to communicate directly to the user in real time, but rather record enough 
information into a log file for an administration to understand how well the 
program is performing and whether anything unusual is happening.

In contrast, *Inform* is meant to used to provide information from command line 
utilities directly to the user in real time. It is not confined to only logging 
events, but instead can be used anywhere the normal Python *print* function 
would be used. In effect, *Inform* allows you to create and use multiple print 
functions each of which is tailored for a specific situation. This of course is 
something you could do yourself using the built-in *print* function, but with 
*Inform* you will not have to embed your print functions in complex condition 
statements, every message is formatted in a consistent manner that follows 
normal Unix conventions, and you can control all of your print functions by 
configuring a single object.


Installation
------------

Install with::

   pip3 install --user inform

Requires Python2.7 or Python3.3 or better.


Just a Taste
------------

*Inform* defines a collection of *print*-like functions that have different 
roles.  These functions are referred to as 'informants' and include include 
*display*, *warn*, *error*, and *fatal*.  All of them take arguments in the same 
manner as Python's built-in print function and all of them write the desired 
message to standard output, with the last three adding a header to the message 
that indicates the type of message.  For example:

.. code-block:: python

    >>> from inform import display, warn, error, fatal
    >>> display(
    ...     'Display is like print',
    ...     'except that it supports logging and can be disabled.')
    Display is like print except that it supports logging and can be disabled.

    >> warn('warnings get a header that is printed in yellow.')
    warning: warnings get a header that is printed in yellow.

    >> error('errors get a header that is printed in red.')
    error: errors get a header that is printed in red.

    >> fatal('fatals are like errors, except that they are, well, fatal.')
    error: fatals are like errors, except that they are, well, fatal.

*fatal* produces the same message as does *error*, but also terminates the 
program.  To make the error messages stand out, the header is generally rendered 
in a color appropriate to the message, so warnings use yellow and errors use 
red.  The headers are only colored if they are being written to a TTY.

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
    ...     display(k=key, v=val, template='{k:>5s} = {v}')
     blue = 3346ff
    green = 4fff33
      red = ff5733

You can every specify a collection of templates. In this case{k: v for k, v in kwargs if v }
The first one for which all keys are known is used.  For example;

    >>> colors = {
    ...     'red': ('ff5733', 'failure'),
    ...     'green': ('4fff33', 'success'),
    ...     'blue': ('3346ff', None),
    ... }

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

Informants also take the named argument *culprit*, which is used to identify the 
object of the message.  For example:

.. code-block:: python

    >>> import os
    >>> filename = 'config'
    >>> if not os.path.exists(filename):
    ...     display('missing.', culprit=filename)
    config: missing.

The *culprit* can also be a tuple:

.. code-block:: python

    >>> line = 5
    >>> display('syntax error.', culprit=(filename, line))
    config, 5: syntax error.

For more control of the informants, you can import and instantiate the *Inform* 
class yourself along with the desired informants.  This gives you the ability to 
specify options:

.. code-block:: python

    >>> from inform import Inform, display, error
    >>> Inform(logfile=False, prog_name="myprog", quiet=True)
    <...>
    >>> display('Initializing ...')

    >>> error('file not found.', culprit='data.in')
    myprog error: data.in: file not found.

An object of the Inform class is referred to as an informer (not to be confused 
with the print functions, which are  referred to as informants). Once 
instantiated, you can use the informer to change various settings, terminate the 
program, or return a count of the number of errors that have occurred.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name=False)
    >>> error('file not found.', culprit='data.in')
    error: data.in: file not found.
    >>> informer.errors_accrued()
    1

Besides the four informant already described, *Inform* provides several others, 
including *log*, *codicil*, *comment*, *narrate*, *output*, *notify*. *debug* 
and *panic*.  Informants in general can write to the log file, to the standard 
output, or to a notifier. They can add headers and specify the color of the 
header and the message. They can also continue the previous message or they can 
terminate the program.  These informants each embody a predefined set of these 
choices. In addition, they can be affected by options passed to the active 
informer. Generally this is used to enable or disable informants based on 
various verbosity options.

At its simplest, *Inform* provides a flexible way of printing user messages.  In 
addition, it provides a collection of utility functions that are often useful 
when constructing messages. For example, *os_error* converts *OSError* exception 
into a simple well formatted string that can be used to describe the exception 
to the user. For example:

.. code-block:: python

    >>> from inform import os_error, error
    >>> try:
    ...     with open(filename) as f:
    ...         config = f.read()
    ... except (OSError, IOError) as e:
    ...     error(os_error(e))
    error: config: no such file or directory.

*Inform* also provides a generic exception that can be used directly or can be 
subclassed to create your own exceptions:

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
   examples
   releases
