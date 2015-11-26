Messenger
=========

A light-weight package with few dependencies that provides various print-like 
functions to communicate to user with logging and output control.

Defines a collection of 'print' functions (messengers) that have different 
roles.  These functions are declared under the Messengers section and include 
*log*, *comment*, *narrate*, *display*, *output*, *debug*, *warn*, *error*, 
*fatal* and *panic*.  Each of these functions takes arguments like the standard 
print function: unnamed arguments must all be strings and they are joined 
together to produce the output, the named arguments act to control the process.  
The available controls (named arguments) are:

sep=' ':
   Specifies the string used to join the unnamed arguments.
end='\\n':
   Specifies a string to append to the message.
file=stdout:
   The destination stream (a file pointer).
flush=False:
   Whether the message should flush the destination stream.
prefix=None:
   A string that is added to the start of a message as a prefix.  It will be 
   separated from the message by a colon.

With the simplest use of the program, you simply import the messengers you need 
and call them (they take the same arguments as does the *print* function built 
in to Python:

.. code-block:: python

    >>> from messenger import output
    >>> output('ice', 9)
    ice 9

More typical is to import and instantiate the Messenger class yourself. This 
gives you the ability to specify the desired options:

.. code-block:: python

    >>> from messenger import Messenger, output
    >>> Messenger(logfile=False)
    <...>
    >>> output('test')
    test

You can also use a *with* statement to invoke the messenger. This closes the 
messenger when the *with* statement terminates (you must not use the messenger 
functions when no messenger is present). This is useful when writing tests. In 
this case you can provide your own output streams so that you can access the 
normally printed output of your code:

.. code-block:: python

    >>> from messenger import Messenger, output
    >>> import io

    >>> def run_test():
    ...     output('running test')

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

    >>> output_text
    'running test\n'

    >>> error_text
    ''

    >>> logfile_text[:10], logfile_text[-13:]
    ('Invoked as', 'running test\n')

You can create your own messengers:

.. code-block:: python

    >>> from messenger import Messenger, MessengerGenerator

    >>> red = MessengerGenerator(message_color='red')
    >>> with Messenger():
    ...     red('Oh No!')
    Oh No!

Several utility functions are provided that are sometimes helpful when creating 
messages.

conjoin(iterable, cong=' and ', sep=', '):
    Like ''.join(), but allows you to specify a conjunction that is placed 
    between the last two elements, ex: conjoin(['a', 'b', 'c'], conj=' or ') 
    generates 'a, b or c'.

cull(collection, remove=None):
    Strips a list of a particular value (remove). By default, it strips a list 
    of Nones. remove may be a function, in which case it takes a single item as 
    an argument and returns True if that item should be removed from the list.

fmt(msg, \*args, \**kwargs):
    Similar to ''.format(), but it can pull arguments from the local scope.

plural(count, singular_form, plural_form=None):
    Produces either the singular or plural form of a word based on a count.
    The count may be an integer, or an iterable, in which case its length is 
    used. If the plural form is not give, the singular form is used with an 's' 
    added to the end.

os_error(exception):
    Generates clean messages for operating system errors.

is_str(obj):
    Returns True if its argument is a string-like object.

is_iterable(obj):
    Returns True if its argument is iterable.

is_collection(obj):
    Returns True if its argument is iterable but is not a string.

For example:

.. code-block:: python

    >>> from messenger import (
    ...     Messenger, output, error, conjoin, cull, fmt, plural, os_error
    ... )

    >>> Messenger(prog_name='myprog')
    <...>
    >>> filenames = cull(['a', 'b', None, 'd'])
    >>> filetype = 'CSV'
    >>> output(
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
    myprog error: a: No such file or directory.
    myprog error: b: No such file or directory.
    myprog error: d: No such file or directory.

*filetype* was passed into *fmt* even though it is not necessary to do so in 
order to work around an issue in doctests. Normally *filetype=filetype* could be 
left out of the arguments to *fmt*.

Finally, an exception, *UserError*, is provided that takes the same arguments as 
a messenger.  This allows you to catch the exception and handle it if you like.  
The exception provides the *report* method that processes the exception as an 
error:

.. code-block:: python

    >>> from messenger import Messenger, UserError

    >>> Messenger(prog_name='myprog')
    <...>
    >>> try:
    ...     raise UserError('must not be zero:', 0)
    ... except UserError as e:
    ...     e.report()
    myprog error: must not be zero: 0

Any keyword arguments provided will be available in *e.kwargs*, but certain 
keyword arguments are reserved by messenger (see above).

Messenger Class
---------------
The Messenger class takes the following arguments:

logfile (string or stream):
   Path to logfile. By default, .<prog_name>.log is used. May also 
   pass an open stream. Pass False if no logfile is desired.
prog_name (string):
   Program name. By default, basename(argv[0]) is used. Use False to indicate 
   that program name should not be added to message headers.
argv (list of strings):
   System command line arguments (logged). By default, sys.argv is used.
version (string):
   Program version (logged if provided).
termination_callback (func):
   A function that is called at program termination.
colorscheme (None, 'light', or 'dark'):
   Color scheme to use. None indicates that messages should not be 
   colorized. Colors are not used if desired output stream is not 
   a TTY.
stdout (stream):
   Messages are sent here by default. Generally used for testing. If 
   not given, sys.stdout is used.
stderr (stream):
   Termination messages are sent here by default. Generally used for 
   testing.  If not given, sys.stderr is used.
\**kwargs:
   Any additional keyword arguments are made attributes that are ignored by 
   Messenger, but may be accessed by the messengers.  The default messages 
   assume the presence of the following additional keyword arguments (if not 
   specified they are assumed to be None):

   mute (bool):
       All output is suppressed except on fatal errors. Logging is also 
       suppressed.
   quiet (bool):
       Normal output is suppressed if this is set (it is still logged)
   verbose (bool):
       Comments are output to user, normally they are just logged.
   narrate (bool):
       Narration is output to user, normally it is just logged.

MessengerGenerator Class
------------------------
The MessengerGenerator class takes the following arguments:

severity=None:
   Messages with severities get headers and the severity acts as label.
is_error=False:
   Message is counted as an error.
log=True:
   Send to the log file, may be a boolean or a function that accepts the 
   messenger as an argument and returns a boolean.
output=True:
   Send to the output stream, may be a boolean or a function that accepts the 
   messenger as an argument and returns a boolean.
terminate=False:
   Terminate the program, exit status is the value of the terminate unless 
   terminate==True, in which case 1 is returned if an error occurred and 
   0 otherwise.
message_color=None:
   Color used to display the message. Choose from *black*, *red*, *green*, 
   *yellow*, *blue*, *magenta*, *cyan*, *white*.
header_color=None:
   Color used to display the header, if one is produced.

Standard Messengers
-------------------

The following messengers are provided. All of the messengers except those that 
process fatal error messages and debugging messages do not produce any output if 
*mute* is set.

.. code-block:: python

   log = MessengerGenerator(
       output=False,
       log=lambda messenger: not messenger.mute,
   )

Saves a message to the log file without displaying it.

.. code-block:: python

   comment = MessengerGenerator(
       output=lambda messenger: messenger.verbose and not messenger.mute,
       log=lambda messenger: not messenger.mute,
       message_color='cyan',
   )

Displays a message only if *verbose* is set. Logs the message. The message is 
displayed in cyan.

.. code-block:: python

   narrate = MessengerGenerator(
       output=lambda messenger: messenger.narrate and not messenger.mute,
       log=lambda messenger: not messenger.mute,
       message_color='blue',
   )

Displays a message only if *narrate* is set. Logs the message. The message is 
displayed in blue.

.. code-block:: python

   display = MessengerGenerator(
       output=lambda messenger: not messenger.quiet and not messenger.mute,
       log=lambda messenger: not messenger.mute,
   )


Displays a message if *quiet* is not set. Logs the message.

.. code-block:: python

   output = MessengerGenerator(
       output=lambda messenger: not messenger.mute,
       log=lambda messenger: not messenger.mute,
   )

Displays and logs a message.

.. code-block:: python

   debug = MessengerGenerator(
       severity='DEBUG',
       output=True,
       log=True,
       header_color='magenta',
   )

Displays and logs a debugging message. A header with the label *DEBUG* is added 
to the message and the header is colored magenta.

Displays and logs a message.

.. code-block:: python

   warn = MessengerGenerator(
       severity='warning',
       header_color='yellow',
       output=lambda messenger: not messenger.mute,
       log=lambda messenger: not messenger.mute,
   )

Displays and logs a warning message. A header with the label *warning* is added 
to the message and the header is colored yellow.

.. code-block:: python

   error = MessengerGenerator(
       severity='error',
       is_error=True,
       header_color='red',
       output=lambda messenger: not messenger.mute,
       log=lambda messenger: not messenger.mute,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red.

.. code-block:: python

   fatal = MessengerGenerator(
       severity='error',
       is_error=True,
       terminate=1,
       header_color='red',
       output=True,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red. The program is terminated with an 
exit status of 1.

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

