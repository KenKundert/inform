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

.. image:: https://img.shields.io/pypi/dd/inform.svg
    :target: https://pypi.python.org/pypi/inform/

| Version: 1.7.0
| Released: 2017-03-17
|

A light-weight package with few dependencies that provides various print-like 
functions to communicate to the user. It also provides logging and output 
control.

Install with::

    pip install inform

Supported in Python2.7, Python3.3, Python3.4, Python3.5, and Python3.6.

This package defines a collection of 'print' functions that have different 
roles.  These functions are referred to as 'informants' and are described below 
in the the Informants section. They include include *log*, *comment*, *codicil*.  
*narrate*, *display*, *output*, *notify*, *debug*, *warn*, *error*, *fatal* and 
*panic*.  Each of these functions takes arguments like the standard print 
function: unnamed arguments are converted to strings and joined together to 
produce the output, the named arguments act to control the process.  The 
available controls (named arguments) are:

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
hanging = *True*:
   Indicates hanging indentation should be used when outputting multi-line 
   message with headers or culprits.

With the simplest use of the program, you simply import the informants you need 
and call them (they take the same arguments as does the *print* function built 
into Python:

.. code-block:: python

    >>> from inform import display
    >>> display('ice', 9)
    ice 9

More typical is to import and instantiate the Inform class yourself along with 
the desired informants.  This gives you the ability to specify options:

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
instantiated, an informer can be used to terminate the program or return a count 
of the number of errors that have occurred.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="prog")
    >>> error('file not found.', culprit='data.in')
    prog error: data.in: file not found.
    >>> informer.errors_accrued()
    1

You can also use a *with* statement to invoke the informer. This closes the 
informer when the *with* statement terminates (you must not use the informants 
when no informer is present). This is useful when writing tests. In this case 
you can provide your own output streams so that you can access the normally 
printed output of your code:

.. code-block:: python

    >>> from inform import Inform, display
    >>> import sys
    >>> if sys.version[0] == '2':
    ...     # io assumes unicode, which python2 does not provide by default
    ...     # so use StringIO instead
    ...     from StringIO import StringIO
    ...     # Add support for with statement by monkeypatching
    ...     StringIO.__enter__ = lambda self: self
    ...     StringIO.__exit__ = lambda self, exc_type, exc_val, exc_tb: self.close()
    ... else:
    ...     from io import StringIO

    >>> def run_test():
    ...     display('running test')

    >>> with StringIO() as stdout, \
    ...      StringIO() as stderr, \
    ...      StringIO() as logfile, \
    ...      Inform(stdout=stdout, stderr=stderr, logfile=logfile) as msg:
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

You can create your own informants:

.. code-block:: python

    >>> from inform import Inform, InformantGenerator

    >>> verbose1 = InformantGenerator(output=lambda m: m.verbosity >= 1)
    >>> verbose2 = InformantGenerator(output=lambda m: m.verbosity >= 2)
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
InformantGenerator when creating the informants.


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


Inform Class
------------
The Inform class controls the active informants. It takes the following 
arguments as options (the value given for the argument is its default):

Arguments
"""""""""

mute=False (bool)
   With the provided informants all output is suppressed when set (it is still 
   logged). This is generally used when the program being run is being run by 
   another program that is generating its own messages and does not want the 
   user confused by additional messages. In this case, the calling program is 
   responsible for observing and reacting to the exit status of the called 
   program.
quiet=False (bool):
   With the provided informants normal output is suppressed when set (it is 
   still logged). This is used when the user has indicated that they are 
   uninterested in any conversational messages and just want to see the 
   essentials (generally error messages).
verbose=False (bool):
   With the provided informants comments are output to user when set; normally 
   they are just logged. Comments are generally used to document unusual 
   occurrences that might warrant the user's attention.
narrate=False (bool):
   With the provided informants narration is output to user when set, normally 
   it is just logged.  Narration is generally used to inform the user as to what 
   is going on. This can help place errors and warnings in context so that they 
   are easier to understand.
logfile=False (string or stream):
   May be a string, in which case it is taken to be the path of the logfile.  
   May be *True*, in which case ./.<prog_name>.log is used.  May be an open 
   stream.  Or it may be *False*, in which case no log file is created.
prog_name=True (string):
   The program name. Is appended to the message headers and used to create the 
   default logfile name. May be a string, in which case it is used as the name 
   of the program.  May be *True*, in which case basename(argv[0]) is used.  May 
   be *False* to indicate that program name should not be added to message 
   headers.
argv=None (list of strings):
   System command line arguments (logged). By default, sys.argv is used. If 
   False is passed in, argv is not logged and argv[0] is not available to be the 
   program name.
version=None (string):
   Program version (logged if provided).
termination_callback=None (func):
   A function that is called at program termination.
colorscheme='dark' (*None*, 'light', or 'dark'):
   Color scheme to use. *None* indicates that messages should not be colorized.  
   Colors are not used if output stream is not a TTY.
flush=False (bool):
   Flush the stream after each write. Is useful if you program is crashing, 
   causing loss of the latest writes. Can cause programs to run considerably 
   slower if they produce a lot of output. Not available with python2.
stdout=None (stream):
   Messages are sent here by default. Generally used for testing. If 
   not given, sys.stdout is used.
stderr=None (stream):
   Termination messages are sent here by default. Generally used for 
   testing.  If not given, sys.stderr is used.
hanging_indent=True (bool):
   Indicates hanging indentation should be used by default when outputting 
   multiline message with headers or culprits.
\**kwargs:
   Any additional keyword arguments are made attributes that are ignored by 
   Inform, but may be accessed by the informants.

Methods
"""""""

The Inform class provides the following user accessible methods. Most of these 
methods are also available as functions, which act on the current informer.

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

   You may also pass a string for the status, in which case the program prints 
   the string to stderr and terminates with an exit status of 1.

terminate_if_errors(status=1):
   Terminate the program with the given exit status if an error has occurred.  

errors_accrued(reset = *False*):
   Return the number of errors that have accrued.

disconnect():
   Deactivate the current Inform, restoring the default.

Functions
"""""""""

Several of the above methods are also available as stand-alone functions that 
act on the currently active informer.  This make it easy to use their 
functionality even if you do not have local access to the informer. They are:

| done()
| terminate()
| terminate_if_errors()
| errors_accrued()

InformantGenerator Class
------------------------
The InformantGenerator class takes the following arguments:

severity = *None*:
   Messages with severities get headers. The header consists of the severity, 
   the program name (if desired), and the culprit (if provided). If the message 
   text does not contain a newline it is appended to the header.  Otherwise the 
   message text is indented and placed on the next line.
is_error = *False*:
   Should message be counted as an error.
log = *True*:
   Send message to the log file. May be a boolean or a function that accepts the 
   Inform object as an argument and returns a boolean.
output = *True*:
   Send to the output stream. May be a boolean or a function that accepts the 
   Inform object as an argument and returns a boolean.
notify = *False*:
   Send message to the notifier.  The notifier will display the message that 
   appears temporarily in a bubble at the top of the screen.  May be a boolean 
   or a function that accepts the informer as an argument and returns a boolean.
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

An object of InformantGenerator is referred to as an informant. It is generally 
treated as a function that is called to produce the desired output.

.. code-block:: python

    >>> from inform import InformantGenerator

    >>> succeed = InformantGenerator(message_color='green')
    >>> fail = InformantGenerator(message_color='red')

    >>> succeed('This message would be green.')
    This message would be green.

    >>> fail('This message would be red.')
    This message would be red.


Standard Informants
-------------------

The following informants are provided. All of the informants except panic and 
debug do not produce any output if *mute* is set.

log
"""

.. code-block:: python

   log = InformantGenerator(
       output=False,
       log=True,
   )

Saves a message to the log file without displaying it.


comment
"""""""

.. code-block:: python

   comment = InformantGenerator(
       output=lambda informer: informer.verbose and not informer.mute,
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

   codicil = InformantGenerator(is_continuation=True)

Continues a previous message. Continued messages inherit the properties (output, 
log, message color, etc) of the previous message.  If the previous message had 
a header, that header is not output and instead the message is indented.

.. code-block:: python

    >>> from inform import Inform, warn, codicil
    >>> informer = Inform(prog_name="myprog")
    >>> warn('file not found.', culprit='ghost')
    myprog warning: ghost: file not found.

    >>> codicil('skipping')
        skipping


narrate
"""""""

.. code-block:: python

   narrate = InformantGenerator(
       output=lambda informer: informer.narrate and not informer.mute,
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

   display = InformantGenerator(
       output=lambda informer: not informer.quiet and not informer.mute,
       log=True,
   )

Displays a message if *quiet* is not set. Logs the message.

.. code-block:: python

    >>> from inform import display
    >>> display('We the people ...')
    We the people ...


output
""""""

.. code-block:: python

   output = InformantGenerator(
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs a message. This is used for messages that are not errors that 
are noteworthy enough that they need to get through even though the user has 
asked for quiet.

.. code-block:: python

    >>> from inform import output
    >>> output('We the people ...')
    We the people ...


notify
""""""

.. code-block:: python

   notify = InformantGenerator(
       notify=True,
       log=True,
   )

Temporarily display the message in a bubble at the top of the screen.  Also 
prints the message on the standard output and sends it to the log file.  This is 
used for messages that the user is otherwise unlikely to see because they have 
no access to the standard output.

.. code-block:: python

    >>> from inform import output
    >>> output('We the people ...')
    We the people ...


debug
"""""

.. code-block:: python

   debug = InformantGenerator(
       severity='DEBUG',
       output=True,
       log=True,
       header_color='magenta',
   )

Displays and logs a debugging message. A header with the label *DEBUG* is added 
to the message and the header is colored magenta.

.. code-block:: python

    >>> from inform import Inform, debug
    >>> informer = Inform(prog_name="myprog")
    >>> debug('HERE!')
    myprog DEBUG: HERE!


warn
""""

.. code-block:: python

   warn = InformantGenerator(
       severity='warning',
       header_color='yellow',
       output=lambda informer: not informer.quiet and not informer.mute,
       log=True,
   )

Displays and logs a warning message. A header with the label *warning* is added 
to the message and the header is colored yellow.

.. code-block:: python

    >>> from inform import Inform, warn
    >>> informer = Inform(prog_name="myprog")
    >>> warn('file not found, skipping.', culprit='ghost')
    myprog warning: ghost: file not found, skipping.


error
"""""

.. code-block:: python

   error = InformantGenerator(
       severity='error',
       is_error=True,
       header_color='red',
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="myprog")
    >>> error('invalid value specified, expected number.', culprit='count')
    myprog error: count: invalid value specified, expected number.

fatal
"""""

.. code-block:: python

   fatal = InformantGenerator(
       severity='error',
       is_error=True,
       terminate=1,
       header_color='red',
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message and the header is colored red. The program is terminated with an 
exit status of 1.


panic
"""""

.. code-block:: python

   panic = InformantGenerator(
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

Several utility functions are provided for your convenience. They are often 
helpful when creating messages.

indent(text, leader='    ',  first=0, stops=1, sep='\n'):
    Indents the text. Multiples of *leader* are added to the beginning of the 
    lines to indent.  *first* is the number of indentations used for the first 
    line relative to the others (may be negative but (first + stops) should not 
    be. *stops* is the default number of indentations to use. *sep* is the 
    string used to separate the lines.

conjoin(iterable, conj=' and ', sep=', '):
    Like ''.join(), but allows you to specify a conjunction that is placed 
    between the last two elements, ex: conjoin(['a', 'b', 'c'], conj=' or ') 
    generates 'a, b or c'.

cull(collection):
    Strips items from a list that have a particular value. By default, it strips 
    a list of values that if casted to a boolean would have a value of False 
    (False, None, '', (), [], etc.).  A particular value may be specified using 
    the 'remove' as a keyword argument.  The value of remove may be a function, 
    in which case it takes a single item as an argument and returns *True* if 
    that item should be removed from the list.

fmt(msg, \*args, \**kwargs):
    Similar to ''.format(), but it can pull arguments from the local scope.

render(obj):
    Recursively convert an object to a string with reasonable formatting.  Has 
    built in support for the base Python types (None, bool, int, float, str, 
    set, tuple, list, and dict).  If you confine yourself to these types, the 
    output of render() can be read by the Python interpreter. Other types are 
    converted to string with repr().

plural(count, singular_form, plural_form = *None*):
    Produces either the singular or plural form of a word based on a count.
    The count may be an integer, or an iterable, in which case its length is 
    used. If the plural form is not give, the singular form is used with an 's' 
    added to the end.

full_stop(string):
    Adds a period to the end of the string if needed (if the last character is 
    not a period, question mark or exclamation mark). It applies str() to its 
    argument, so it is generally a suitable replacement for str in 
    str(exception) when trying extract an error message from an exception.

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

    >>> from inform import Inform, display, error, conjoin, cull, fmt, plural, os_error

    >>> Inform(prog_name=False)
    <...>
    >>> filenames = cull(['a', 'b', None, 'd'])
    >>> filetype = 'CSV'
    >>> display(
    ...     fmt(
    ...         'Reading {filetype} {files}: {names}.',
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
    >>> display('D', '=', render(D))
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

The Color class has the concept of a colorscheme. There are three supported 
schemes: *None*, light, and dark. With *None* the text is not colored. In 
general it is best to use the light colorscheme on dark backgrounds and the dark 
colorscheme on light backgrounds.

The Color class takes the following arguments when creating a colorizer:

color:
   Render the text in the specified color. Choose from *None*, 'black', 'red', 
   'green', 'yellow', 'blue', 'magenta', 'cyan' or 'white'.

scheme = 'dark':
   Use the specified colorscheme when rendering the text.
   Choose from *None*, 'light' or 'dark'.

enable = True:
   If set to False, the colorizer does not render the text in color.

A colorizer takes the following arguments:

text:
   The text to be colored.

scheme = *False*:
   Use to override the colorscheme when rendering the text.  Choose from *None*, 
   *False*, 'light' or 'dark'.  If you specify *False* (the default), the 
   colorscheme specified when creating the colorizer is used.


Colorizers have one user settable attribute: *enable*. By default *enable* is 
True. If you set it to *False* the colorizer no longer renders the text in 
color:

.. code-block:: python

   >> warning = Color('yellow', enable=Color.isTTY(sys.stdout))
   >> warning('Cannot find precusor, ignoring.')
   Cannot find precusor, ignoring.

The Color class has the following class methods:

isTTY(stream):
   Takes a stream as an argument (default is stdout) and returns true if it is 
   a TTY.  A typical use is:

.. code-block:: python

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

strip_colors(text):
   Takes a string as its input and return that string stripped of any color 
   codes.
