Quicksilver Messenger Service
=============================

A light-weight package with few dependencies that provides various print-like 
functions to communicate to the user. It also provides logging and output 
control.

Install with::

    pip install messenger

This package defines a collection of 'print' functions (messengers) that have 
different roles.  These functions are declared under the Messengers section and 
include *log*, *comment*, *codicil*. *narrate*, *display*, *output*, *debug*, 
*warn*, *error*, *fatal* and *panic*.  Each of these functions takes arguments 
like the standard print function: unnamed arguments are converted to strings and 
joined together to produce the output, the named arguments act to control the 
process.  The available controls (named arguments) are:

sep = ' ':
   Specifies the string used to join the unnamed arguments.
end = '\\n':
   Specifies a string to append to the message.
file = stdout:
   The destination stream (a file pointer).
flush = *False*:
   Whether the message should flush the destination stream (not available in 
   python2).
culprit = *None*:
   A string that is added to the beginning of the message that identifies the 
   culprit (the object for which the problem being reported was found). May also 
   be a collection of strings, in which case they are joined with '.'.

With the simplest use of the program, you simply import the messengers you need 
and call them (they take the same arguments as does the *print* function built 
into Python:

.. code-block:: python

    >>> from messenger import display
    >>> display('ice', 9)
    ice 9

More typical is to import and instantiate the Messenger class yourself along 
with the desired messengers.  This gives you the ability to specify options:

.. code-block:: python

    >>> from messenger import Messenger, display
    >>> Messenger(logfile=False)
    <...>
    >>> display('test')
    test

You can also use a *with* statement to invoke the messenger. This closes the 
messenger when the *with* statement terminates (you must not use the messenger 
functions when no messenger is present). This is useful when writing tests. In 
this case you can provide your own output streams so that you can access the 
normally printed output of your code:

.. code-block:: python

    >>> from messenger import Messenger, display
    >>> import io

    >>> def run_test():
    ...     display('running test')

    >>> with io.StringIO() as stdout, \
    ...      io.StringIO() as stderr, \
    ...      io.StringIO() as logfile, \
    ...      Messenger(stdout=stdout, stderr=stderr, logfile=logfile) as msg:
    ...         run_test()
    ...
    ...         num_errors = msg.errors_accrued()
    ...         output_text = stdout.getvalue()
    ...         error_text = stderr.getvalue()
    ...         logfile_text = logfile.getvalue()

    >>> num_errors
    0

    >>> str(output_text)
    'running test\n'

    >>> str(error_text)
    ''

    >>> str(logfile_text[:10]), str(logfile_text[-13:])
    ('Invoked as', 'running test\n')

You can create your own messengers:

.. code-block:: python

    >>> from messenger import Messenger, MessengerGenerator

    >>> verbose1 = MessengerGenerator(output=lambda m: m.verbosity >= 1)
    >>> verbose2 = MessengerGenerator(output=lambda m: m.verbosity >= 2)
    >>> with Messenger(verbosity=0):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')

    >>> with Messenger(verbosity=1):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')
    First level of verbosity.

    >>> with Messenger(verbosity=2):
    ...     verbose1('First level of verbosity.')
    ...     verbose2('Second level of verbosity.')
    First level of verbosity.
    Second level of verbosity.

The argument *verbosity* is not an explicitly supported argument to Messenger.  
In this case Messenger simply saves the value and makes it available as an 
attribute, and it is this attribute that is queried by the lambda function 
passed to the MessengerGenerator when creating the messengers.


Exception
---------
An exception, *Error*, is provided that takes the same arguments as a messenger.  
This allows you to catch the exception and handle it if you like.  The exception 
provides the *report* and *terminate* methods that processes the exception as an 
error or fatal error if you find that you can do nothing else with the 
exception:

.. code-block:: python

    >>> from messenger import Messenger, Error

    >>> Messenger(prog_name='myprog')
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
keyword arguments are reserved by messenger (see above).


Messenger Class
---------------
The Messenger class controls the active messengers. It takes the following 
arguments as options:

mute (bool)
   With the provided messengers all output is suppressed when set (it is still 
   logged). This is generally used when the program being run is being run by 
   another program that is generating its own messages and does not want the 
   user confused by additional messages. In this case, the calling program is 
   responsible for observing and reacting to the exit status of the called 
   program.
quiet (bool):
   With the provided messengers normal output is suppressed when set (it is 
   still logged). This is used when the user has indicated that they are 
   uninterested in any conversational messages and just want to see the 
   essentials (generally error messages).
verbose (bool):
   With the provided messengers comments are output to user when set; normally 
   they are just logged. Comments are generally used to document unusual 
   occurrences that might warrant the user's attention.
narrate (bool):
   With the provided messengers narration is output to user when set, normally 
   it is just logged.  Narration is generally used to inform the user as to what 
   is going on. This can help place errors and warnings in context so that they 
   are easier to understand.
logfile (string or stream):
   May be a string, in which case it is taken to be the path of the logfile.  
   May be *True*, in which case ./.<prog_name>.log is used.  May be an open 
   stream.  Or it may be *False*, in which case no log file is created.
prog_name (string):
   The program name. Is appended to the message headers and used to create the 
   default logfile name. May be a string, in which case it is used as the name 
   of the program.  May be *True*, in which case basename(argv[0]) is used.  May 
   be *False* to indicate that program name should not be added to message 
   headers.
argv (list of strings):
   System command line arguments (logged). By default, sys.argv is used. If 
   False is passed in, argv is not logged and argv[0] is not available to be the 
   program name.
version (string):
   Program version (logged if provided).
termination_callback (func):
   A function that is called at program termination.
colorscheme (*None*, 'light', or 'dark'):
   Color scheme to use. *None* indicates that messages should not be colorized.  
   Colors are not used if output stream is not a TTY.
flush (bool):
   Flush the stream after each write. Is useful if you program is crashing, 
   causing loss of the latest writes. Can cause programs to run considerably 
   slower if they produce a lot of output. Not available with python2.
stdout (stream):
   Messages are sent here by default. Generally used for testing. If 
   not given, sys.stdout is used.
stderr (stream):
   Termination messages are sent here by default. Generally used for 
   testing.  If not given, sys.stderr is used.
\**kwargs:
   Any additional keyword arguments are made attributes that are ignored by 
   Messenger, but may be accessed by the messengers.

The Messenger class provides the following user accessible methods. Most of 
these methods are also available as functions, which act on the current 
Messenger.

set_logfile():
   Allows you to change the logfile (only available as a method).

done():
   Terminates the program normally (exit status is 0).

terminate(status = *None*):
   Terminate the program with the given exit status. If specified, the exit 
   status should be a positive integer less than 128. Usually, the following 
   values are used:

   | 0: success  
   | 1: unexpected error 
   | 2: invalid invocation
   | 3: panic

   If the exit status is not specified, then the exit status is set to 1 if an 
   error occurred and 0 otherwise.

terminate_if_errors(status=1):
   Terminate the program with the given exit status if an error has occurred.  

errors_accrued():
   Return the number of errors that have accrued.

disconnect():
   Deactivate the current Messenger, restoring the default.


MessengerGenerator Class
------------------------
The MessengerGenerator class takes the following arguments:

severity = *None*:
   Messages with severities get headers. The header consists of the severity, 
   the program name (if desired), and the culprit (if provided). If the message 
   text does not contain a newline it is appended to the header.  Otherwise the 
   message text is indented and placed on the next line.
is_error = *False*:
   Should message be counted as errors.
log = *True*:
   Send message to the log file. May be a boolean or a function that accepts the 
   Messenger object as an argument and returns a boolean.
output = *True*:
   Send to the output stream. May be a boolean or a function that accepts the 
   Messenger object as an argument and returns a boolean.
terminate = *False*:
   Terminate the program, exit status is the value of the terminate unless 
   *terminate* is *True*, in which case 1 is returned if an error occurred and 
   0 otherwise.
is_continuation = *False*:
   This message is a continuation of the previous message.  It will use the 
   properties of the previous message (output, log, message color, etc) and if 
   the previous message had a header, that header is not output and instead the 
   message is indented.
message_color = *None*:
   Color used to display the message. Choose from *black*, *red*, *green*, 
   *yellow*, *blue*, *magenta*, *cyan*, *white*.
header_color = *None*:
   Color used to display the header, if one is produced.


Standard Messengers
-------------------

The following messengers are provided. All of the messengers except panic and 
debug do not produce any output if *mute* is set.


log
"""

.. code-block:: python

   log = MessengerGenerator(
       output=False,
       log=True,
   )

Saves a message to the log file without displaying it.


comment
"""""""

.. code-block:: python

   comment = MessengerGenerator(
       output=lambda messenger: messenger.verbose and not messenger.mute,
       log=True,
       message_color='cyan',
   )

Displays a message only if *verbose* is set. Logs the message. The message is 
displayed in cyan.

Comments are generally used to document unusual occurrences that might warrant 
the user's attention.

codicil
"""""""

.. code-block:: python

   codicil = MessengerGenerator(is_continuation=True)

Continues a previous message. Continued messages inherit the properties (output, 
log, message color, etc) of the previous message.  If the previous message had 
a header, that header is not output and instead the message is indented.


narrate
"""""""

.. code-block:: python

   narrate = MessengerGenerator(
       output=lambda messenger: messenger.narrate and not messenger.mute,
       log=True,
       message_color='blue',
   )

Displays a message only if *narrate* is set. Logs the message. The message is 
displayed in blue.

Narration is generally used to inform the user as to what is going on. This can 
help place errors and warnings in context so that they are easier to understand.
Distinguishing narration from comments allows them to colored differently and 
controlled separately.


display
"""""""

.. code-block:: python

   display = MessengerGenerator(
       output=lambda messenger: not messenger.quiet and not messenger.mute,
       log=True,
   )


Displays a message if *quiet* is not set. Logs the message.


output
""""""

.. code-block:: python

   output = MessengerGenerator(
       output=lambda messenger: not messenger.mute,
       log=True,
   )

Displays and logs a message. This is used for messages that are not errors that 
are noteworthy enough that they need to get through even though the user has 
asked for quiet.


debug
"""""

.. code-block:: python

   debug = MessengerGenerator(
       severity='DEBUG',
       output=True,
       log=True,
       header_color='magenta',
   )

Displays and logs a debugging message. A header with the label *DEBUG* is added 
to the message and the header is colored magenta.


warn
""""

.. code-block:: python

   warn = MessengerGenerator(
       severity='warning',
       header_color='yellow',
       output=lambda messenger: not messenger.quiet and not messenger.mute,
       log=True,
   )

Displays and logs a warning message. A header with the label *warning* is added 
to the message and the header is colored yellow.


error
"""""

.. code-block:: python

   error = MessengerGenerator(
       severity='error',
       is_error=True,
       header_color='red',
       output=lambda messenger: not messenger.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red.


fatal
"""""

.. code-block:: python

   fatal = MessengerGenerator(
       severity='error',
       is_error=True,
       terminate=1,
       header_color='red',
       output=lambda messenger: not messenger.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red. The program is terminated with an 
exit status of 1.


panic
"""""

.. code-block:: python

   panic = MessengerGenerator(
       severity='internal error (please report)',
       is_error=True,
       terminate=3,
       header_color='red',
       output=True,
       log=True,
   )

Displays and logs a panic message. A header with the label *internal error* is 
added to the message and the header is colored red. The program is terminated 
with an exit status of 3.


Utilities
---------

Several utility functions are provided that are sometimes helpful when creating 
messages.

conjoin(iterable, conj=' and ', sep=', '):
    Like ''.join(), but allows you to specify a conjunction that is placed 
    between the last two elements, ex: conjoin(['a', 'b', 'c'], conj=' or ') 
    generates 'a, b or c'.

cull(collection, remove = *None*):
    Strips a list of a particular value (remove). By default, it strips a list 
    of Nones. remove may be a function, in which case it takes a single item as 
    an argument and returns *True* if that item should be removed from the list.

fmt(msg, \*args, \**kwargs):
    Similar to ''.format(), but it can pull arguments from the local scope.

plural(count, singular_form, plural_form = *None*):
    Produces either the singular or plural form of a word based on a count.
    The count may be an integer, or an iterable, in which case its length is 
    used. If the plural form is not give, the singular form is used with an 's' 
    added to the end.

os_error(exception):
    Generates clean messages for operating system errors.

is_str(obj):
    Returns *True* if its argument is a string-like object.

is_iterable(obj):
    Returns *True* if its argument is iterable.

is_collection(obj):
    Returns *True* if its argument is iterable but is not a string.

For example:

.. code-block:: python

    >>> from messenger import (
    ...     Messenger, display, error, conjoin, cull, fmt, plural, os_error
    ... )

    >>> Messenger(prog_name=False)
    <...>
    >>> filenames = cull(['a', 'b', None, 'd'])
    >>> filetype = 'CSV'
    >>> display(
    ...     fmt(
    ...         'Reading {filetype} {files}: {names}.',
    ...         filetype=filetype,  # see comment below
    ...         files=plural(filenames, 'file'),
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

*filetype* was passed into *fmt* even though it is not necessary to do so in 
order to work around an issue in doctests. Normally *filetype=filetype* could be 
left out of the arguments to *fmt*.

Color Class
"""""""""""

The Color class creates colorizers, which are used to render text in 
a particular color.  They are like the Python print function in that they take 
any number of unnamed arguments that are converted to strings and then join into 
a single string. The string is then coded for the chosen color and returned. For 
example::

   >> from messenger import Color, display

   >> green = Color('green')
   >> red = Color('red')
   >> success = green('pass:')
   >> failure = red('FAIL:')

   >> failures = {'outrigger': True, 'signalman': False}
   >> for name, fails in failures.iters():
   ..     result = failure if fails else success
   ..     display(result, name)
   FAIL: outrigger
   pass: signalman

When the messages print, the 'pass:' will be green and 'FAIL:' will be red.
    
The Color class has the concept of a colorscheme. There are three supported 
schemes: *None*, light, and dark. With *None* the text is not colored. In 
general it is best to use the light colorscheme on dark backgrounds and the dark 
colorscheme on light backgrounds.

The Color class takes the following arguments when creating a colorizer:

color:
   Render the text in the specified color. Choose from *None*, 'black', 'red', 
   'green', 'yellow', 'blue', 'magenta', 'cyan' or 'white'.

colorscheme = 'dark':
   Use the specified colorscheme when rendering the text.
   Choose from *None*, 'light' or 'dark'.

A colorizer takes the following arguments:

text:
   The text to be colored.

colorscheme = *False*:
   Use to override the colorscheme when rendering the text.  Choose from *None*, 
   *False*, 'light' or 'dark'.  If you specify *False* (the default), the 
   colorscheme specified when creating the colorizer is used.

Colorizers have one user settable attribute: *enable*. By default *enable* is 
True. If you set it to *False* the colorizer no longer renders the text in 
color.

The Color class has the following class methods:

isTTY:
   Takes a stream as an argument and returns true if it is a TTY. A typical use 
   is::

      fail = Color('red')
      fail.active = Color.isTTY(sys.stdout))

strip_colors:
   Takes a string as its input and return that text stripped of any color codes.
