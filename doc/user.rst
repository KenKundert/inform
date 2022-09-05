.. currentmodule:: inform

.. Initialize Inform and suppress outputting of program name

    >>> from inform import Inform, Color
    >>> inform = Inform(prog_name=False)


User's Guide
============

.. _using informants:

Using Informants
----------------

This package defines a collection of 'print' functions that are referred to as 
informants.  They include include :ref:`log informant`, :ref:`comment 
informant`, :ref:`codicil informant`, :ref:`narrate informant`, :ref:`display 
informant`, :ref:`output informant`, :ref:`notify informant`, :ref:`debug 
informant`, :ref:`warn informant`, :ref:`error informant`, :ref:`fatal 
informant` and :ref:`panic informant`.

They all take arguments in a manner that is a generalization of Python's 
built-in print function.  Each of the informants is used for a specific purpose, 
but they all take and process arguments in the same manner.  These functions are 
distinguished in the :ref:`predefined informants` section.  In this section, the 
manner in which they process their arguments is presented.

With the simplest use of the program, you simply import the informants you need 
and call them, placing those things that you wish to print in the argument list 
as unnamed arguments:

.. code-block:: python

    >>> from inform import display
    >>> display('ice', 9)
    ice 9

Informant Arguments
"""""""""""""""""""

By default, all of the unnamed arguments converted to strings and then joined 
together using a space between each argument.  However, you can use named 
arguments to change this behavior.  The following named arguments are used to 
control the informants:

sep = ' ':
   Specifies the string used to join the unnamed arguments.

end = '\\n':
   Specifies a string to append to the message.

file:
   The destination stream (a file pointer).

flush = *False*:
   Whether the message should flush the destination stream (not available in 
   python2).

culprit = *None*:
   A string that is added to the beginning of the message that identifies the 
   culprit (the object for which the problem being reported was found). May also 
   be a number or a tuple that contains strings and numbers. If *culprit* is 
   a tuple, the members are converted to strings and joined with *culprit_sep* 
   (default is ', ').

codicil = *None*:
   A string or a collection of strings that contain messages that are printed 
   after the primary message.

wrap = False:
   Specifies whether message should be wrapped. *wrap* may be True, in which 
   case the default width of 70 is used.  Alternately, you may specify the 
   desired width. The wrapping occurs on the final message after the arguments 
   have been joined.

template = None:
   A template that if present interpolates the arguments to form the final 
   message rather than simply joining the unnamed arguments with *sep*. The 
   template is a string, and its *format* method is called with the unnamed and 
   named arguments of the message passed as arguments. *template* may also be 
   a collection of strings, in which case the first template for which all the 
   necessary arguments are available is used.

remove:
   Specifies the argument values that are unavailable to the template.

The first four are also accepted by Python's built-in *print* function and have 
the same behavior.

This example makes use of the *sep* and *end* named arguments:

..  code-block:: python

   >>> from inform import display

   >>> actions = ['r: rewind', 'p: play/pause', 'f: fast forward']
   >>> display('The choices include', *actions, sep=',\n    ', end='.\n')
   The choices include,
       r: rewind,
       p: play/pause,
       f: fast forward.

.. _culprits:

Culprits
""""""""

*culprit* is used to identify the target of the message. If the message is 
pointing out a problem, the *culprit* is generally the source of the problem.

Here is a simple example:

..  code-block:: python

   >>> from inform import error

   >>> error('file not found.', culprit='now-playing')
   error: now-playing: file not found.

Here is an example that demonstrates the wrap and composite culprit features:

..  code-block:: python

   >>> value = -1
   >>> error(
   ...     'Encountered illegal value',
   ...     value,
   ...     'when filtering.  Consider regenerating the dataset.',
   ...     culprit=('input.data', 32), wrap=True,
   ... )
   error: input.data, 32:
       Encountered illegal value -1 when filtering.  Consider regenerating
       the dataset.

Occasionally the actual culprits are not available where the messages are 
printed.  In this case you can use culprit caching.  Simply cache the culprits 
in you informer using :func:`set_culprit` or :func:`add_culprit` and then recall 
them when needed using :func:`get_culprit`.  Both *set_culprit* and 
*add_culprit* are designed to be used with Python's *with* statement.

The following example illustrates the used of culprit caching. Here, the code is 
spread over several functions, and the various culprits are known locally but 
are not passed directly into the function that may report the error. Rather than 
explicitly passing the culprits into the various functions, which would clutter 
up their argument lists, the culprits are cached in case they are needed.

..  code-block:: python

   >>> from inform import add_culprit, get_culprit, set_culprit, error

   >>> def read_param(line, parameters):
   ...    name, value = line.split(' = ')
   ...    try:
   ...        parameters[name] = float(value)
   ...    except ValueError:
   ...        error(
   ...            'expected a number, found:', value,
   ...            culprit=get_culprit(name)
   ...        )

   >>> def read_params(lines):
   ...    parameters = {}
   ...    for lineno, line in enumerate(lines):
   ...        with add_culprit(lineno+1):
   ...            read_param(line, parameters)

   >>> filename = 'parameters'
   >>> with open(filename) as f, set_culprit(filename):
   ...    lines = f.read().splitlines()
   ...    parameters = read_params(lines)
   error: parameters, 3, c: expected a number, found: ack


Templates
"""""""""

The *template* strings are the same as one would use with Python's built-in 
format function and string method (as described in `Format String Syntax 
<https://docs.python.org/3/library/string.html#format-string-syntax>`_).  The 
*template* string can interpolate either named or unnamed arguments.  In this 
example, named arguments are interpolated:

.. code-block:: python

    >>> colors = {
    ...     'red': ('ff5733', 'failure'),
    ...     'green': ('4fff33', 'success'),
    ...     'blue': ('3346ff', None),
    ... }

    >>> for key in sorted(colors.keys()):
    ...     val = colors[key]
    ...     display(k=key, v=val, template='{k:>5s} = {v[0]}')
     blue = 3346ff
    green = 4fff33
      red = ff5733

You can also specify a collection of templates.  The first one for which all 
keys are available is used.  For example;

.. code-block:: python

    >>> for name in sorted(colors.keys()):
    ...     code, desc = colors[name]
    ...     display(name, code, desc, template=('{:>5s} = {}  — {}', '{:>5s} = {}'))
     blue = 3346ff
    green = 4fff33  — success
      red = ff5733  — failure

    >>> for name in sorted(colors.keys()):
    ...     code, desc = colors[name]
    ...     display(k=name, v=code, d=desc, template=('{k:>5s} = {v}  — {d}', '{k:>5s} = {v}'))
     blue = 3346ff
    green = 4fff33  — success
      red = ff5733  — failure

The first loop interpolates positional (unnamed) arguments, the second 
interpolates the keyword (named) arguments.

By default, the values that are considered unavailable and so will invalidate 
a template are those that would be False when cast to a Boolean.  So, by 
default, the following values are considered unavailable: 0, False, None, '', 
(), [], {}, etc.  You can use the *remove* named argument to control this.  
*remove* may be a function, a collection, or a scalar.  The function would take 
a single argument that is the value to consider and return True if the value
should be unavailable. The scalar or the collection simply specifies the value 
or values that should be unavailable.

.. code-block:: python

    >>> accounts = dict(checking=1100, savings=0, brokerage=None)

    >>> for name, amount in sorted(accounts.items()):
    ...     display(name, amount, template=('{:>10s} = ${}', '{:>10s} = NA'), remove=None)
     brokerage = NA
      checking = $1100
       savings = $0


.. _predefined informants:

Predefined Informants
---------------------

The following informants are predefined in *Inform*. You can create custom 
informants using :class:`InformantFactory`.

All of the informants except :ref:`panic informant` and :ref:`debug informant` 
do not produce any output if *mute* is set.


.. _log informant:

log
"""

.. code-block:: python

   log = InformantFactory(
       output=False,
       log=True,
   )

Saves a message to the log file without displaying it.


.. _comment informant:

comment
"""""""

.. code-block:: python

   comment = InformantFactory(
       output=lambda informer: informer.verbose and not informer.mute,
       log=True,
       message_color='cyan',
   )

Displays a message only if *verbose* is set. Logs the message. The message is 
displayed in cyan when writing to the console.

Comments are generally used to document unusual occurrences that might warrant 
the user's attention.


.. _codicil informant:

codicil
"""""""

.. code-block:: python

   codicil = InformantFactory(is_continuation=True)

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


.. _narrate informant:

narrate
"""""""

.. code-block:: python

   narrate = InformantFactory(
       output=lambda informer: informer.narrate and not informer.mute,
       log=True,
       message_color='blue',
   )

Displays a message only if *narrate* is set. Logs the message. The message is 
displayed in blue when writing to the console.

Narration is generally used to inform the user as to what is going on. This can 
help place errors and warnings in context so that they are easier to understand.
Distinguishing narration from comments allows them to colored differently and 
controlled separately.


.. _display informant:

display
"""""""

.. code-block:: python

   display = InformantFactory(
       output=lambda informer: not informer.quiet and not informer.mute,
       log=True,
   )

Displays a message if *quiet* is not set. Logs the message.

.. code-block:: python

    >>> from inform import display
    >>> display('We the people ...')
    We the people ...


.. _output informant:

output
""""""

.. code-block:: python

   output = InformantFactory(
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs a message. This is used for messages that are not errors and 
that are noteworthy enough that they need to get through even though the user 
has asked for quiet.

.. code-block:: python

    >>> from inform import output
    >>> output('The sky is falling!')
    The sky is falling!


.. _notify informant:

notify
""""""

.. code-block:: python

   notify = InformantFactory(
       notify=True,
       log=True,
   )

Temporarily display the message in a bubble at the top of the screen.  Also 
sends it to the log file.  This is used for messages that the user is otherwise 
unlikely to see because they have no access to the standard output.

When using notify you may pass in the *urgency* named argument to specify the 
urgency of the notification. Its value must 'low', 'normal', or 'critical' or it 
will be ignored.


.. _debug informant:

debug
"""""

.. code-block:: python

   debug = InformantFactory(
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

Generally one does not use the *debug* informant directly. Instead one uses the 
available debugging functions: :func:`aaa()`, :func:`ddd()`, :func:`ppp()`, 
:func:`sss()` and :func:`vvv()`.


.. _warn informant:

warn
""""

.. code-block:: python

   warn = InformantFactory(
       severity='warning',
       header_color='yellow',
       output=lambda informer: not informer.quiet and not informer.mute,
       log=True,
   )

Displays and logs a warning message. A header with the label *warning* is added 
to the message. The header is colored yellow when writing to the console.

.. code-block:: python

    >>> from inform import Inform, warn
    >>> informer = Inform(prog_name="myprog")
    >>> warn('file not found, skipping.', culprit='ghost')
    myprog warning: ghost: file not found, skipping.


.. _error informant:

error
"""""

.. code-block:: python

   error = InformantFactory(
       severity='error',
       is_error=True,
       header_color='red',
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message. The header is colored red when writing to the console.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="myprog")
    >>> error('invalid value specified, expected a number.', culprit='count')
    myprog error: count: invalid value specified, expected a number.


.. _fatal informant:

fatal
"""""

.. code-block:: python

   fatal = InformantFactory(
       severity='error',
       is_error=True,
       terminate=1,
       header_color='red',
       output=lambda informer: not informer.mute,
       log=True,
   )

Displays and logs an error message. A header with the label *error* is added to 
the message.  The header is colored red when writing to the console. The program 
is terminated with an exit status of 1.

.. code-block:: python

    >> from inform import fatal, os_error
    >> try:
    ..     with open('config') as f:
    ..         read_config(f.read())
    .. except OSError as e:
    ..     fatal(os_error(e), codicil='Cannot continue.')
    myprog error: config: file not found
        Cannot continue.

.. _panic informant:

panic
"""""

.. code-block:: python

   panic = InformantFactory(
       severity='internal error (please report)',
       is_error=True,
       terminate=3,
       header_color='red',
       output=True,
       log=True,
   )

Displays and logs a panic message. A header with the label *internal error* is 
added to the message.  The header is colored red when writing to the console.  
The program is terminated with an exit status of 3.


Modifying Existing Informants
"""""""""""""""""""""""""""""

You may adjust the behavior of existing informants by overriding the attributes 
that were passed in when they were created.  For example, in many cases you 
might prefer that normal program output is not logged, either because it is 
voluminous or because it is sensitive. In that case you can simply override the 
*log* attributes for the *display* and *output* informants like so:

.. code-block:: python

   from inform import display, output
   display.log = False
   output.log = False

Any attribute that can be passed into :class:`InformantFactory` when creating an 
informant can be overridden. However, when overriding a color you must use 
a colorizer rather than a color name:

.. code-block:: python

    from inform import comment, Color
    comment.message_color=Color('cyan')


.. informers:

Informant Control
-----------------

For more control of the informants, you can import and instantiate the 
:class:`Inform` class along with the desired informants.  This gives you the 
ability to specify options:

.. code-block:: python

    >>> from inform import Inform, display, error
    >>> Inform(logfile=False, prog_name=False, quiet=True)
    <...>

    >>> display('hello')

    >>> error('file not found.', culprit='data.in')
    error: data.in: file not found.

In this example the *logfile* argument disables opening and writing to the 
logfile.  The *prog_name* argument stops *Inform* from adding the program name 
to the error message. And *quiet* turns off non-essential output, and in this 
case it causes the output of *display* to be suppressed.

An object of the Inform class is referred to as an informer (not to be confused 
with the print functions, which are  referred to as informants). Once 
instantiated, you can use the informer to change various settings, terminate the 
program, return a count of the number of errors that have occurred, etc.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="prog")

    >>> error('file not found.', culprit='data.in')
    prog error: data.in: file not found.

    >>> informer.errors_accrued()
    1

You can also use a *with* statement to invoke the informer. This activates the 
informer for the duration of the *with* statement, returning to the previous 
informer when the *with* statement terminates. This is useful when writing 
tests.  In this case you can provide your own output streams so that you can 
access the normally printed output of your code:

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

    >>> str(logfile_text.strip().split('\n')[-1])
    'running test'


Logfiles
""""""""

To configure *Inform* to generate a logfile you can specify the logfile to 
:class:`Inform` or to :meth:`Inform.set_logfile`.  The logfile can be specified 
as a string, a *pathlib.Path*, an open stream, or as a Boolean. If *True*, 
a logfile is created and named *./<prog_name>.log*.  If *False*, no logfile is 
created.  In addition, if you want to defer the decision on what should be the 
logfile without losing the log messages that occur before the ultimate 
destination of those messages is set, you can use an instance of 
:class:`LoggingCache`, which simply saves the messages in memory until it is
replaced, at which point they are transferred to the new logfile.  For example:

.. code-block:: python

    >>> from inform import Inform, LoggingCache, log, indent
    >>> with Inform(logfile=LoggingCache()) as inform:
    ...     log("This message is cached.")
    ...     inform.set_logfile(".mylog")
    ...     log("This message is not cached.")

    >>> with open(".mylog") as f:
    ...     print("Contents of logfile:")
    ...     print(indent(f.read()), end='')  # +ELLIPSIS
    Contents of logfile:
        ...
        This message is cached.
        This message is not cached.

An existing logfile will be renamed before creating the logfile if you specify 
*prev_logfile_suffix* to :class:`Inform`.


Message Destination
"""""""""""""""""""

You can specify the output stream when creating an informant. If you do not, 
then the stream uses is under the control of *Inform's* *stream_policy* 
argument.

If *stream_policy* is set to 'termination', then all messages are sent to the 
standard output except the final termination message, which is set to standard 
error.  This is suitable for programs whose output largely consists of status 
messages rather than data, and so would be unlikely to be used in a pipeline. 

If *stream_policy* is 'header'. then all messages with headers (those messages 
produced from informants with *severity*) are sent to the standard error stream 
and all other messages are sent to the standard output. This is more suitable 
for programs whose output largely consists of data and so would likely be used 
in a pipeline.

It is also possible for *stream_policy* to be a function that takes three 
arguments, the informant and the standard output and error streams. It should 
return the desired stream.

If *True* is passed to the *notify_if_no_tty* *Inform* argument, then error 
messages are sent to the notifier if the standard output is not a TTY.


.. user define informants:

User Defined Informants
-----------------------

You can create your own informants using :class:`InformantFactory`. One 
application of this is to support multiple levels of verbosity. To do this, an 
informant would be created for each level of verbosity, as follows:

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

The argument *verbosity* is not an explicitly supported argument of 
:class:`Inform`.  In this case *Inform* simply saves the value and makes it 
available as an attribute, and it is this attribute that is queried by the 
lambda function passed to *InformantFactory* when creating the informants.

Another use for user-defined informants is to create print functions that output 
is a particular color:

.. code-block:: python

    >>> from inform import InformantFactory

    >>> succeed = InformantFactory(message_color='green')
    >>> fail = InformantFactory(message_color='red')

    >>> succeed('This message would be green.')
    This message would be green.

    >>> fail('This message would be red.')
    This message would be red.

A common use for this would be to have success and failure messages. For 
example, if your program runs a series of tests, the successes could be printed 
in green and the failures in red. In addition, the success informant may be 
configured to suppress the messages if the user asks for quiet.  In that case, 
only the failures would be displayed.

.. _inform exceptions:

Exceptions
----------

An exception, :class:`Error`, is provided that takes the same arguments as an 
informant.  This allows you to catch the exception and handle it if you like.  
Any arguments you pass into the exception are retained and are available when 
processing the exception.  The exception provides the :meth:`Error.report` and 
:meth:`Error.terminate` methods that processes the exception as an error or 
fatal error if you find that you can do nothing else with the exception.

.. code-block:: python

    >>> from inform import Inform, Error

    >>> Inform(prog_name='myprog')
    <...>
    >>> try:
    ...     raise Error('must not be zero.', culprit='naught')
    ... except Error as e:
    ...     e.report()
    myprog error: naught: must not be zero.

Besides *culprit*, you can use any of the named arguments accepted by 
informants. In addition, you can also use *informant* as a named argument.  
*informant* changes the informant that is used when reporting the error. It is 
often used to convert an exception to a warning or to a fatal error. For 
example:

.. code-block:: python

    >>> from inform import Inform, Error, warn

    >>> Inform(prog_name='myprog')
    <...>
    >>> def read_files(filenames):
    ...     files = {}
    ...     for filename in filenames:
    ...        try:
    ...            with open(filename) as f:
    ...                files[filename] = f.read()
    ...        except FileNotFoundError:
    ...            raise Error('missing.', culprit=filename, informant=warn)
    ...     return files

    >>> filenames = 'parameters swallows worlds'.split()
    >>> try:
    ...     files = read_files(filenames)
    ... except Error as e:
    ...     files = None
    ...     e.report()
    myprog warning: worlds: missing.

:class:`Error` also provides :meth:`Error.get_message()` and 
:meth:`Error.get_culprit()` methods, which return the message and the culprit.  
You can also cast the exception to a string or call the :meth:`Error.render()` 
method to get a string that contains both the message and the culprit formatted 
so that it can be shown to the user.

All positional arguments are available in *e.args* and any keyword arguments 
provided are available in *e.kwargs*.

One common approach to using :class:`Error` is to pass all the arguments that 
make up the error message as arguments and then assemble them into the message 
by providing a template.  In that way the arguments are directly available to 
the handler if needed. For example:

.. code-block:: python

    >>> from difflib import get_close_matches
    >>> from inform import Error, codicil, conjoin, fmt

    >>> known_names = 'alpha beta gamma delta epsilon'.split()
    >>> name = 'alfa'

    >>> try:
    ...     if name not in known_names:
    ...         raise Error(name, choices=known_names, template="name '{}' is not defined.")
    ... except Error as e:
    ...     candidates = get_close_matches(e.args[0], e.choices, 1, 0.6)
    ...     candidates = conjoin(candidates, conj=' or ')
    ...     e.report()
    ...     codicil(fmt('Did you mean {candidates}?'))
    myprog error: name 'alfa' is not defined.
        Did you mean alpha?

Notice that useful information (*choices*) is passed into the exception that may 
be useful when processing the exception even though it is not incorporated into 
the message.

You can override the template by passing a new one to 
:meth:`Error.get_message()` or :meth:`Error.render()`.  With
:meth:`Error.report()` or :meth:`Error.terminate()` you can override any named 
argument, such as *template* or *culprit*.  This can be helpful if you need to 
translate a message or change it to make it more meaningful to the end user:

.. code-block:: python

    >>> try:
    ...     raise Error(name, template="name '{}' is not defined.")
    ... except Error as e:
    ...     e.report(template="'{}' ist nicht definiert.")
    myprog error: 'alfa' ist nicht definiert.

You can catch an :class:`Error` exception and then reraise it after
modifying its named arguments using :meth:`Error.reraise()`.  This is
helpful when all the information needed for the error message is not available
where the initial exception is detected. Typically new culprits or codicils are
added. For example, in the following the filename is added to the exception
using *reraise* in *parse_file*:

.. code-block:: python

    >>> def parse_lines(lines):
    ...     values = {}
    ...     for i, line in enumerate(lines):
    ...         try:
    ...             k, v = line.split()
    ...         except ValueError:
    ...             raise Error('syntax error.', culprit=i+1)
    ...         values[k] = v
    ...     return values

    >>> def parse_file(filename):
    ...     try:
    ...         with open(filename) as f:
    ...             return parse_lines(f.read().splitlines())
    ...     except Error as e:
    ...         e.reraise(culprit=e.get_culprit(filename))

    >>> try:
    ...     unladen_airspeed = parse_file('swallows')
    ... except Error as e:
    ...     e.report()
    myprog error: swallows, 2: syntax error.

This example uses :meth:`Error.get_culprit()` to access the existing culprit or 
culprits of the exception. Regardless of how many there are, they are always 
returned as a culprit. It also accepts a culprit as an argument, which is 
returned along with and before the culprit from the exception.

Also available is :meth:`Error.get_codicil()`, which behaves similarly except 
with codicils rather than culprits and the argument is added after the codicil 
from the exception rather than before.


Subclassing Error
"""""""""""""""""

When creating subclasses of :class:`Error` you can add a template to the 
subclass as a way of specifying the error message or messages that are to be 
used for that exception. For example:

.. code-block:: python

    >>> class InvalidValueError(Error):
    ...     template = 'invalid value.'

    >>> try:
    ...     raise InvalidValueError()
    ... except Error as e:
    ...     e.report()
    myprog error: invalid value.

You can include named and unnamed arguments of the exception in the template:

.. code-block:: python

    >>> class InvalidValueError(Error):
    ...     template = 'must not be {}.'

    >>> try:
    ...     raise InvalidValueError('negative', culprit='rate')
    ... except Error as e:
    ...     e.report()
    myprog error: rate: must not be negative.

You can also specify a list of templates that are tried in order, the first for 
which all arguments are available is used:

.. code-block:: python

    >>> class InvalidValueError(Error):
    ...     template = [
    ...         '{} must fall between {min} and {max}.',
    ...         '{} must be greater than {min}.',
    ...         '{} must be less than {max}.',
    ...         '{} must not be {illegal}.',
    ...         '{} must be {legal}.',
    ...         '{} is invalid.',
    ...         'invalid value.',
    ...     ]

    >>> rate = -1.0
    >>> try:
    ...     if rate < 0:
    ...         raise InvalidValueError(rate, illegal='negative', culprit='rate')
    ... except Error as e:
    ...     e.report()
    myprog error: rate: -1.0 must not be negative.


Utilities
---------

Several utility functions are provided for your convenience. They are often 
helpful when creating messages.


.. _color desc:

Color Class
"""""""""""

The :class:`Color` class creates colorizers, which are functions used to render 
text in a particular color.  They combine their arguments in a manner very 
similar to an :ref:`informant <using informants>` and returns the result as 
a string, except the string is coded for the chosen color.  Uses the *sep*, 
*template* and *wrap* keyword arguments to combine the arguments.

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

The Color class has the concept of a colorscheme. There are four supported 
schemes: *None*, *True*, 'light', and 'dark'. With *None* the text is not 
colored, with *True* the colorscheme of the currently active informer is used.
In general it is best to use the 'light' colorscheme on dark backgrounds and the 
'dark' colorscheme on light backgrounds.  You can pass in the colorscheme using 
the *scheme* argument either to the color class or to the colorizer.

Colorizers have one user settable attribute: *enable*. By default *enable* is 
*True*. If you set it to *False* the colorizer no longer renders the text in 
color:

.. code-block:: python

   >> warning = Color('yellow')
   >> warning('This will be yellow on the console.')
   This will be yellow on the console.

   >> warning.enable = False
   >> warning('This will not be yellow.')
   This will not be yellow.

Alternatively, you can enable or disable the colorizer when creating it. This 
example uses the :meth:`Color.isTTY()` method to determine whether the output 
stream, the standard output by default, is a console.

.. code-block:: python

   >> warning = Color('yellow', enable=Color.isTTY())
   >> warning('Cannot find precursor, ignoring.')
   Cannot find precursor, ignoring.


.. _columns desc:

columns
"""""""

.. py:function:: columns(array, pagewidth=79, alignment='<', leader='    ')
   :noindex:

:func:`columns` distributes the values of an array over enough columns to fill 
the screen.

This example prints out the phonetic alphabet:

.. code-block:: python

    >>> from inform import columns

    >>> title = 'Display the NATO phonetic alphabet.'
    >>> words = """
    ...     Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett Kilo
    ...     Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform
    ...     Victor Whiskey X-ray Yankee Zulu
    ... """.split()

    >>> display(title, columns(words), sep='\n')
    Display the NATO phonetic alphabet.
        Alfa      Echo      India     Mike      Quebec    Uniform   Yankee
        Bravo     Foxtrot   Juliett   November  Romeo     Victor    Zulu
        Charlie   Golf      Kilo      Oscar     Sierra    Whiskey
        Delta     Hotel     Lima      Papa      Tango     X-ray


.. _conjoin desc:

conjoin
"""""""

.. py:function:: conjoin(iterable, conj=' and ', sep=', ', fmt=None)
   :noindex:

:func:`conjoin` is like ''.join(), but allows you to specify a conjunction that 
is placed between the last two elements. For example:

.. code-block:: python

    >>> from inform import conjoin
    >>> conjoin(['a', 'b', 'c'])
    'a, b and c'

    >>> conjoin(['a', 'b', 'c'], conj=' or ')
    'a, b or c'

If you prefer the use of the Oxford comma, you can add it as follow:

.. code-block:: python

    >>> conjoin(['a', 'b', 'c'], conj=', and ')
    'a, b, and c'

You can specify a format string that is applied to every item in the list before 
they are joined:

.. code-block:: python

    >>> conjoin([10.1, 32.5, 16.9], fmt='${:0.2f}')
    '$10.10, $32.50 and $16.90'


.. _cull desc:

cull
""""

.. py:function:: cull(collection, [remove])
   :noindex:

:func:`cull` strips items from a collection that have a particular value.  The 
collection may be list-like (*list*, *tuple*, *set*, etc.) or a dictionary-like 
(*dict*, *OrderedDict*).  A new collection of the same type is returned with the 
undesirable values removed.

By default, :func:`cull` strips values that would be *False* when cast to 
a Boolean (0, *False*, *None*, '', (), [], etc.).  A particular value may be 
specified using the *remove* as a keyword argument.  The value of *remove* may 
be a collection, in which case any value in the collection is removed, or it may 
be a function, in which case it takes a single item as an argument and returns 
*True* if that item should be removed from the list.

.. code-block:: python

    >>> from inform import cull, display
    >>> display(*cull(['a', 'b', '', 'd']), sep=', ')
    a, b, d

    >>> accounts = dict(checking=1100.16, savings=13948.78, brokerage=0)
    >>> for name, amount in sorted(cull(accounts).items()):
    ...     display(name, amount, template='{:>10s}: ${:,.2f}')
      checking: $1,100.16
       savings: $13,948.78


.. _did_you_mean desc:

did_you_mean
""""""""""""

.. py:function:: did_you_mean(candidate, choices)
   :noindex:

    Given a candidate string from the user, return the closest valid choice.

    Args:
        candidate (string):
            The string given by the user.
        choices (iterable):
            The set of valid strings that the user was expected to choose from.

    Examples:

        >>> from inform import did_you_mean
        >>> did_you_mean('cat', ['cat', 'dog'])
        'cat'
        >>> did_you_mean('car', ['cat', 'dog'])
        'cat'
        >>> did_you_mean('car', {'cat': 1, 'dog': 2})
        'cat'


.. _fmt desc:

fmt
"""

.. py:function:: fmt(msg, \*args, \**kwargs)
   :noindex:

:func:`fmt` is similar to ''.format(), but it can pull arguments from the local 
scope.

.. code-block:: python

    >>> from inform import conjoin, display, fmt

    >>> filenames = ['a', 'b', 'c', 'd']
    >>> filetype = 'CSV'
    >>> display(
    ...     fmt(
    ...         'Reading {filetype} files: {names}.',
    ...         names=conjoin(filenames),
    ...     )
    ... )
    Reading CSV files: a, b, c and d.

Notice that *filetype* was not explicitly passed into *fmt()* even though it was 
explicitly called out in the format string.  *filetype* can be left out of the 
argument list because if *fmt* does not find a named argument in its argument 
list, it will look for a variable of the same name in the local scope.


.. _format_range desc:

format_range
""""""""""""

.. py:function:: format_range(items)
   :noindex:

func:`format_range` can be used to create a succinct, readable string 
representing a set of numbers.

.. code-block:: python

    >>> from inform import format_range
    >>> format_range({1, 2, 3, 5})
    '1-3,5'


.. _full_stop desc:

full_stop
"""""""""

.. py:function:: full_stop(string)
   :noindex:

:func:`full_stop` adds a period to the end of the string if needed (if the last 
character is not a period, question mark or exclamation mark). It applies str() 
to its argument, so it is generally a suitable replacement for str in 
str(exception) when trying extract an error message from an exception.

This is generally useful if you need to print a string that should have 
punctuation, but may not.

.. code-block:: python

    >>> from inform import Error, error, full_stop

    >>> found = 0
    >>> try:
    ...     if found is False:
    ...         raise Error('not found', culprit='marbles')
    ...     elif found < 3:
    ...         raise Error('insufficient number.', culprit='marbles')
    ...     raise Error('not found', culprit='marbles')
    ... except Error as e:
    ...     error(full_stop(e))
    myprog error: marbles: insufficient number.


.. _indent desc:

indent
""""""

.. py:function:: indent(text, leader='    ',  first=0, stops=1, sep='\\n')
   :noindex:

:func:`indent` indents *text*. Multiples of *leader* are added to the beginning 
of the lines to indent.  *first* is the number of indentations used for the 
first line relative to the others (may be negative but (first + stops) should 
not be.  *stops* is the default number of indentations to use. *sep* is the 
string used to separate the lines.

.. code-block:: python

    >>> from inform import display, indent
    >>> text = 'a b'.replace(' ', '\n')
    >>> display(indent(text))
        a
        b

    >>> display(indent(text, first=1, stops=0))
        a
    b

    >>> display(indent(text, leader='.   ', first=-1, stops=2))
    .   a
    .   .   b


.. _info desc:

Info Class
""""""""""

The :class:`Info` class is intended to be used as a helper class.  When 
instantiated, it converts provided keyword arguments to attributes. Unknown 
attributes evaluate to None. *Info* can be used directly, or it can be used as 
a base class.

.. code-block:: python

    >>> from inform import display, Info
    >>> class Orwell(Info):
    ...     pass

    >>> george = Orwell(peace='war', truth='lies')
    >>> display(str(george))
    Orwell(peace='war', truth='lies')

    >>> display(george.peace)
    war

    >>> display(george.happiness)
    None


.. _is_collection desc:

is_collection
"""""""""""""

.. py:function:: is_collection(obj)
   :noindex:

:func:`is_collection` returns *True* if its argument is a collection.  This 
includes objects such as lists, tuples, sets, dictionaries, etc.  It does not 
include strings.

.. code-block:: python

    >>> from inform import is_collection

    >>> is_collection('')  # string
    False

    >>> is_collection([])  # list
    True

    >>> is_collection(())  # tuple
    True

    >>> is_collection({})  # dictionary
    True

.. _is_iterable desc:

is_iterable
"""""""""""

.. py:function:: is_iterable(obj)
   :noindex:

:func:`is_iterable` returns *True* if its argument is a collection or a string.

.. code-block:: python

    >>> from inform import is_iterable

    >>> is_iterable('abc')
    True

    >>> is_iterable(['a', 'b', 'c'])
    True


.. _is_mapping desc:

is_mapping
""""""""""

.. py:function:: is_mapping(obj)
   :noindex:

:func:`is_collection` returns *True* if its argument is a mapping.  This 
includes dictionary and other dictionary-like objects.

.. code-block:: python

    >>> from inform import is_mapping

    >>> is_mapping('')  # string
    False

    >>> is_mapping([])  # list
    False

    >>> is_mapping(())  # tuple
    False

    >>> is_mapping({})  # dictionary
    True


.. _is_str desc:

is_str
""""""

.. py:function:: is_str(obj)
   :noindex:

:func:`is_str` returns *True* if its argument is a string-like object.

.. code-block:: python

    >>> from inform import is_str

    >>> is_str('abc')
    True

    >>> is_str(['a', 'b', 'c'])
    False


.. _join desc:


join
""""

.. py:function:: join(\*args, \**kwargs)
   :noindex:

:func:`join` combines the arguments in a manner very similar to an 
:ref:`informant <using informants>` and returns the result as a string.  Uses 
the *sep*, *template* and *wrap* keyword arguments to combine the arguments.


.. code-block:: python

    >>> from inform import display, join

    >>> accounts = dict(checking=1100.16, savings=13948.78, brokerage=0)
    >>> lines = []
    >>> for name in sorted(accounts):
    ...     lines.append(join(name, accounts[name], template='{:>10s}: ${:,.2f}'))

    >>> display(*lines, sep='\n')
     brokerage: $0.00
      checking: $1,100.16
       savings: $13,948.78


.. _os_error desc:

os_error
""""""""

.. py:function:: os_error(exception)
   :noindex:

:func:`os_error` generates clean messages for operating system errors.

.. code-block:: python

    >>> from inform import error, os_error

    >>> try:
    ...     with open('temperatures.csv') as f:
    ...         contents = f.read()
    ... except OSError as e:
    ...     error(os_error(e))
    myprog error: temperatures.csv: no such file or directory.


.. _parse_range desc:

parse_range
"""""""""""

.. py:function:: parse_range(items)
   :noindex:

func:`parse_range` can be used to parse sets of numbers from user-inputted 
strings.

.. code-block:: python

    >>> from inform import parse_range
    >>> parse_range('1-3,5')
    {1, 2, 3, 5}


.. _progressbar desc:

ProgressBar Class
"""""""""""""""""

The :class:`ProgressBar` class is used to draw a progress bar as a single text 
line. The line counts down as progress is made and reaches 0 as the task 
completes.  Interruptions are handled with grace.

There are three typical ways to use the progress bar. The first is used to 
illustrate the progress of an iterator. The iterator must have a length.  For 
example:

.. code-block:: python

    >>> from inform import ProgressBar

    >>> processed = []
    >>> def process(item):
    ...     # this function would implement some expensive operation
    ...     processed.append(item)
    >>> items = ['i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9', 'i10']

    >>> for item in ProgressBar(items, prefix='Progress: ', width=60):
    ...     process(item)
    Progress: ⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅0

    >>> display('Processed:', conjoin(processed), end='.\n')
    Processed: i1, i2, i3, i4, i5, i6, i7, i8, i9 and i10.

The second is similar to the first, except you just give an integer to indicate 
how many iterations you wish:

.. code-block:: python

    >>> for i in ProgressBar(50, prefix='Progress: '):
    ...     process(i)
    Progress: ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0

Finally, the third illustrates progress through a continuous range:

.. code-block:: python

    >>> stop = 1e-6
    >>> step = 1e-9

    >>> with ProgressBar(stop) as progress:
    ...     display('Progress:')
    ...     value = 0
    ...     while value <= stop:
    ...         progress.draw(value)
    ...         value += step
    Progress:
    ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅⋅0

In this case, you need to notify the progress bar if you decide to exit the loop 
before its complete unless an exception is raised that causes the *with* block 
to exit:

.. code-block:: python

    >>> with ProgressBar(stop) as progress:
    ...     display('Progress:')
    ...     value = 0
    ...     while value <= stop:
    ...         progress.draw(value)
    ...         value += step
    ...         if value > stop/2:
    ...             progress.escape()
    ...             break
    Progress:
    ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅

Without calling escape, the bar would have been terminated with a 0 upon exiting 
the *with* block. Using *escape()* is not necessary if the *with* block is 
exited via an exception:

.. code-block:: python

    >>> try:
    ...     with ProgressBar(stop) as progress:
    ...         display('Progress:')
    ...         value = 0
    ...         while value <= stop:
    ...             progress.draw(value)
    ...             value += step
    ...             if value > stop/2:
    ...                 raise Error('early exit.')
    ... except Error as e:
    ...     e.report()
    Progress:
    ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅⋅
    myprog error: early exit.

It is possible to pass a second argument to :meth:`ProgressBar.draw()` that 
indicates the desired marker to use when updating the bar.  This is usually used 
to signal that there was a problem with the update.  To do so, you define the 
desired markers when instantiating :class:`ProgressBar`.  Each
marker consists of a fill character and a color.  The color can be specified 
by giving its name, with a :class:`Color` object, or with None.
For example, the following example uses markers to distinguish four types of 
results: *okay*, *warn*, *fail*, *error*.

.. code-block:: python

    >>> results = 'okay okay okay fail okay fail okay error warn okay'.split()

    >>> def process(index):
    ...     # this function would implement some expensive operation
    ...     return results[index]

    >>> markers = dict(
    ...     okay=('⋅', None),
    ...     warn=('−', None),
    ...     fail=('+', None),
    ...     error=('×', None)
    ... )

    >>> with ProgressBar(len(results), prefix="progress: ", markers=markers) as progress:
    ...     for i in range(len(results)):
    ...         status = results[i]
    ...         progress.draw(i+1, status)
    progress: ⋅⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅⋅7++++++6⋅⋅⋅⋅⋅⋅5++++++4⋅⋅⋅⋅⋅⋅3××××××2−−−−−−1⋅⋅⋅⋅⋅⋅0

In this case color was not used, but you could specify the following to render 
the markers in color:

.. code-block:: python

    >>> markers = dict(
    ...     okay=('⋅', 'green'),
    ...     warn=('–', 'yellow'),
    ...     fail=('+', 'magenta'),
    ...     error=('×', 'red')
    ... )

You can also use the :class:`Color` class:

.. code-block:: python

    >>> markers = dict(
    ...     okay=('⋅', Color('green', Color.isTTY())),
    ...     warn=('–', Color('yellow', Color.isTTY())),
    ...     fail=('+', Color('magenta', Color.isTTY())),
    ...     error=('×', Color('red', Color.isTTY()))
    ... )

The progress bar generally handles interruptions with grace. For example:

.. code-block:: python

    >>> for item in ProgressBar(items, prefix='Progress: ', width=60):
    ...     if item == 'i4':
    ...         warn('bad value.', culprit=item)
    Progress: ⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7
    myprog warning: i4: bad value.
    Progress: ⋅⋅⋅⋅⋅9⋅⋅⋅⋅⋅8⋅⋅⋅⋅⋅7⋅⋅⋅⋅⋅6⋅⋅⋅⋅⋅5⋅⋅⋅⋅⋅4⋅⋅⋅⋅⋅3⋅⋅⋅⋅⋅2⋅⋅⋅⋅⋅1⋅⋅⋅⋅⋅0

Notice that the warning started on a new line and the progress bar was restarted 
from the beginning after the warning.

Generally the progress bar is not printed if no tasks were performed. In some 
cases you would like to associate a progress bar with an iterator, and then 
decide later whether there are any tasks that require processing. That could be 
handled as follows:

.. code-block:: python

    >>> with ProgressBar(items, prefix='Progress: ') as progress:
    ...     for i, item in enumerate(items):
    ...         if item.startswith('i'):
    ...             continue
    ...         progress.draw(i)
    ...         process(item)

In this example, every item starts with 'i' and so is skipped. The result is 
that no items are processed and so the progress bar is not printed.

.. _plural desc:

plural
""""""

.. py:class:: plural(count, num='#')
   :noindex:

    Used with python format strings to conditionally format a phrase depending
    on whether it refers to a singular or plural number of things.

    The format specification has three sections, separated by '/'.  The first
    section is always included, the last section is included if the given number
    is plural, and the middle section, which can be omitted, is included if the
    given number is singular.  If there is only one section, it is used as is
    for the singular case and an 's' is added to it for the plural case.
    If any of the sections contain a '#', it is replaced by the number of
    things.

    You may provide either a number (e.g. 0, 1, 2, ...) or any object that
    implements `__len__()` (e.g. list, dict, set, ...).  In the latter case,
    the length of the object will be used to decide whether to use the singular
    of plural form.  Only 1 is considered to be singular; every other number is
    considered plural.

    If the format string starts with '!' then it is removed and the sense of
    plurality is reversed (the plural form is used for one thing, and the
    singular form is used otherwise). This is useful when pluralizing verbs.

    Here is a typical usage::

        >>> from inform import plural, conjoin

        >>> astronauts = ['John Glenn']
        >>> f"The {plural(astronauts):astronaut/s}: {conjoin(astronauts)}"
        'The astronaut: John Glenn'

        >>> astronauts = ['Neil Armstrong', 'Buzz Aldrin', 'Michael Collins']
        >>> f"The {plural(astronauts):astronaut/s}: {conjoin(astronauts)}"
        'The astronauts: Neil Armstrong, Buzz Aldrin and Michael Collins'

    The count can be inserted into the output by placing # into the format 
    specification.

    If using '#' or '!' is inconvenient, you can change them by specifying the 
    *num* or *invert* to *plural()*.

    Examples::

        >>> f"{plural(1):# thing}"
        '1 thing'
        >>> f"{plural(2):# thing}"
        '2 things'

        >>> f"{plural(1):# thing/s}"
        '1 thing'
        >>> f"{plural(2):# thing/s}"
        '2 things'

        >>> f"{plural(1):/a cactus/# cacti}"
        'a cactus'
        >>> f"{plural(2):/a cactus/# cacti}"
        '2 cacti'

        >>> f"{plural(1):# /is/are}"
        '1 is'
        >>> f"{plural(2):# /is/are}"
        '2 are'

        >>> f"{plural([]):# thing/s}"
        '0 things'
        >>> f"{plural([0]):# thing/s}"
        '1 thing'

        >>> f"{plural(1):!agree}"
        'agrees'
        >>> f"{plural(2):!agree}"
        'agree'

    Finally, you can use the *format* method to directly produce a descriptive 
    string::

        >>> plural(2).format("/a cactus/# cacti")
        '2 cacti'

    The original implementation is from `Veedrac
    <http://stackoverflow.com/questions/21872366/plural-string-formatting>`_.


.. _render desc:

render
""""""

.. py:function:: render(obj, sort=None, level=0, tab='    ')
   :noindex:

:func:`render` recursively converts an object to a string with reasonable 
formatting.  Has built in support for the base Python types (*None*, *bool*, 
*int*, *float*, *str*, *set*, *tuple*, *list*, and *dict*).  If you confine 
yourself to these types, the output of :func:`render` can be read by the Python 
interpreter. Other types are converted to string with *repr()*. The dictionary 
keys and set values are sorted if sort is *True*. Sometimes this is not possible 
because the values are not comparable, in which case render reverts to the 
natural order.

This example prints several Python data types:

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

    >>> E={'s': s1, 'n': n, 'S': S, 'L': L, 'd':d, 'D':D}
    >>> display('E', '=', render(E, True))
    E = {
        'D': {
            'L': [
                'alpha string',
                42,
                {'alpha string', 'beta string'},
            ],
            'S': {'alpha string', 'beta string'},
            'd': {1: 'alpha string', 2: 'beta string'},
            'n': 42,
            's': 'alpha string',
        },
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


In addition, you can add support for *render* to your classes by adding one or 
both of these methods:

    _inform_get_args(): returns a list of argument values.

    _inform_get_kwargs(): returns a dictionary of keyword arguments.

.. code-block:: python

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


.. _render_bar desc:

render_bar
""""""""""

.. py:function:: render_bar(normalized_value, width=72)
   :noindex:

:func:`render_bar()` produces a graphic representation of a normalized value in 
the form of a bar.  *normalized_value* is the value to render; it is expected to 
be a value between 0 and 1.  *width* specifies the maximum width of the line in 
characters.

.. code-block:: python

    >>> from inform import render_bar, display
    >>> for i in range(10):
    ...     value = 1 - i/9.02
    ...     display('{:0.3f}: {}'.format(value, render_bar(value, 70)))
    1.000: ██████████████████████████████████████████████████████████████████████
    0.889: ██████████████████████████████████████████████████████████████▏
    0.778: ██████████████████████████████████████████████████████▍
    0.667: ██████████████████████████████████████████████▋
    0.557: ██████████████████████████████████████▉
    0.446: ███████████████████████████████▏
    0.335: ███████████████████████▍
    0.224: ███████████████▋
    0.113: ███████▉
    0.002: ▏


.. _title_case desc:

title_case
""""""""""

.. py:function:: title_case(string, exceptions=(...))
   :noindex:

:func:`title_case` converts the initial letters in the words of a string to 
upper case while maintaining any letters that are already upper case, such as 
acronyms.  Common 'small' words are excepted and words within quotes are handled 
properly.

.. code-block:: python

    >>> from inform import title_case
    >>> headline = 'CDC warns about "aggressive" rats as coronavirus shuts down restaurants'
    >>> display(title_case(headline))
    CDC Warns About "Aggressive" Rats as Coronavirus Shuts Down Restaurants


Debugging Functions
-------------------

The debugging functions are intended to be used when you want to print something 
out when debugging your program.  They are colorful to make it easier to find 
them among the program's normal output, and a header is added that describes 
the location they were called from. This makes it easier to distinguish several 
debug message and also makes it easy to find and remove the functions once you 
are done debugging.


.. _aaa desc:

aaa
"""

.. py:function:: aaa(arg)
   :noindex:

:func:`aaa` prints and then returns its argument.  The argument may be name or 
unnamed.  If named, the name is used as a label when printing the value of the 
argument.  It can be used to print the value of a term within an expression 
without being forced to replicate that term.

In the following example, a critical statement is instrumented to show the 
intermediate values in the computation.  In this case it would be difficult to 
see these intermediate values by replicating code, as calls to the *update* 
method has the side effect of updating the state of the integrator.

.. code:: python

    >>> from inform import aaa, display
    >>> class Integrator:
    ...    def __init__(self, ic=0):
    ...        self.state = ic
    ...    def update(self, vin):
    ...        self.state += vin
    ...        return self.state

    >>> int1 = Integrator(1)
    >>> int2 = Integrator()
    >>> vin = 1
    >>> vout = 0
    >>> for t in range(1, 3):
    ...    vout = 0.7*aaa(int2=int2.update(aaa(int1=int1.update(vin-vout))))
    ...    display('vout = {}'.format(vout))
    myprog DEBUG: <doctest user.rst[...]>, 2, __main__: int1: 2
    myprog DEBUG: <doctest user.rst[...]>, 2, __main__: int2: 2
    vout = 1.4
    myprog DEBUG: <doctest user.rst[...]>, 2, __main__: int1: 1.6
    myprog DEBUG: <doctest user.rst[...]>, 2, __main__: int2: 3.6
    vout = 2.52


.. _ddd desc:

ddd
"""

.. py:function:: ddd(\*args, \*\*kwargs)
   :noindex:

:func:`ddd` pretty prints all of both its unnamed and named arguments.

.. code:: python

    >>> from inform import ddd
    >>> a = 1
    >>> b = 'this is a test'
    >>> c = (2, 3)
    >>> d = {'a': a, 'b': b, 'c': c}
    >>> ddd(a, b, c, d)
    myprog DEBUG: <doctest user.rst[...]>, 1, __main__:
        1
        'this is a test'
        (2, 3)
        {
            'a': 1,
            'b': 'this is a test',
            'c': (2, 3),
        }

If you give named arguments, the name is prepended to its value:

.. code:: python

    >>> from inform import ddd
    >>> ddd(a=a, b=b, c=c, d=d, s='hey now!')
    myprog DEBUG: <doctest user.rst[...]>, 1, __main__:
        a = 1
        b = 'this is a test'
        c = (2, 3)
        d = {
            'a': 1,
            'b': 'this is a test',
            'c': (2, 3),
        }
        s = 'hey now!'

If an arguments has a __dict__ attribute, it is printed rather than the 
argument itself.

.. code:: python

    >>> from inform import ddd

    >>> class Info:
    ...     def __init__(self, **kwargs):
    ...         self.__dict__.update(kwargs)
    ...         ddd(self=self)

    >>> contact = Info(email='ted@ledbelly.com', name='Ted Ledbelly')
    myprog DEBUG: <doctest user.rst[...]>, 4, __main__.Info.__init__():
        self = Info object containing {
            'email': 'ted@ledbelly.com',
            'name': 'Ted Ledbelly',
        }


.. _ppp desc:

ppp
"""

.. py:function:: ppp(\*args, \*\*kwargs)
   :noindex:

:func:`ppp` is very similar to the normal Python print function in that it 
prints out the values of the unnamed arguments under the control of the named 
arguments. It also takes the same named arguments as ``print()``, such as 
``sep`` and ``end``.

If given without unnamed arguments, it will just print the header, which 
good way of confirming that a line of code has been reached.

.. code:: python

    >>> from inform import ppp
    >>> a = 1
    >>> b = 'this is a test'
    >>> c = (2, 3)
    >>> d = {'a': a, 'b': b, 'c': c}
    >>> ppp(a, b, c)
    myprog DEBUG: <doctest user.rst[...]>, 1, __main__: 1 this is a test (2, 3)


.. _sss desc:

sss
"""

.. py:function:: sss()
   :noindex:

:func:`sss` prints a stack trace, which can answer the *How did I get here?* 
question better than a simple print function.

.. code:: python

    >> from inform import sss

    >> def foo():
    ..     sss()
    ..     print('CONTINUING')

    >> foo()
    DEBUG: <doctest user.rst[...]>:2, __main__.foo():
        Traceback (most recent call last):
            ...
    CONTINUING

.. _vvv desc:

vvv
"""

.. py:function:: vvv(\*args)
   :noindex:

:func:`vvv` prints variables from the calling scope. If no arguments are given, 
then all the variables are printed. You can optionally give specific variables 
on the argument list and only those variables are printed.

.. code:: python

    >>> from inform import vvv

    >>> vvv(b, d)
    myprog DEBUG: <doctest user.rst[...]>, 1, __main__:
        b = 'this is a test'
        d = {
            'a': 1,
            'b': 'this is a test',
            'c': (2, 3),
        }

This last feature is not completely robust. The checking is done by value, 
so if several variables share the value of one requested, they are all 
shown.

.. code:: python

    >>> from inform import vvv

    >>> aa = 1
    >>> vvv(a)
    myprog DEBUG: <doctest user.rst[...]>, 1, __main__:
        a = 1
        aa = 1
        vin = 1


.. _site customization:

Site Customization
""""""""""""""""""

Many people choose to add the importing of the debugging function to their 
usercustomize.py file. In this way, the debugging functions are always available 
without the need to explicitly import them. To accomplish this, create 
a *usercustomize.py* files that contains the following and place it in your 
site-packages directory:

.. code:: python

    # Include Inform debugging routines
    try:                 # python3
        import builtins
    except ImportError:  # python2
        import __builtin__ as builtins

    try:
        from inform import aaa, ddd, ppp, sss, vvv
        builtins.aaa = aaa
        builtins.ddd = ddd
        builtins.ppp = ppp
        builtins.sss = sss
        builtins.vvv = vvv
    except ImportError:
        pass

The path of this file is typically 
*~/.local/lib/pythonN.M/site-packages/usercustomize.py* where *M.N* is the 
version number of your python.


Inform Helper Functions
-----------------------

An informer (an :class:`Inform` object) provides a number of useful methods. 
However, it is common that the informer is not locally available.  To avoid the 
clutter that would be created by passing the informer around to where ever  it 
is needed, *Inform* gives you several alternate ways of accessing these methods.  
Firstly is :func:`get_informer()`, which simply returns the currently active 
informer.  Secondly, *Inform* provides a collection of functions that provide 
direct access to the corresponding methods on the currently active informer. 
They are:


done
""""

.. py:function:: done(exit=True)
   :noindex:


:func:`done` terminates the program with the normal exit status. It calls 
:meth:`Inform.done` for the active informer.

If the *exit* argument is False, preparations are made for exiting, but 
*sys.exit* is not called. Instead, the desired exit status is returned.


terminate
"""""""""

.. py:function:: terminate(status=None, exit=True)
   :noindex:

:func:`terminate` terminates the program with specified exit status or message.  
It calls :meth:`Inform.terminate` for the active informer.  

*status* may be an integer, boolean, string, or None. An exit status of 1 is 
used if True or a string is passed in. If None is passed in then 1 is used for 
the exit status if an error was reported and 0 otherwise.

If the *exit* argument is False, preparations are made for exiting, but 
*sys.exit* is not called. Instead, the desired exit status is returned.


terminate_if_errors
"""""""""""""""""""

.. py:function:: terminate_if_errors(status=None, exit=True)
   :noindex:

:func:`terminate_if_errors` terminates the program with specified exit status or 
message if an error was previously reported.  It calls 
:meth:`Inform.terminate_if_errors` for the active informer.

*status* may be an integer, boolean, or string. An exit status of 1 is used if 
True or a string is passed in.

If the *exit* argument is False, preparations are made for exiting, but 
*sys.exit* is not called. Instead, the desired exit status is returned.


errors_accrued
""""""""""""""

.. py:function:: errors_accrued(reset=False)
   :noindex:


:func:`errors_accrued` returns the number of errors that have been reported.  It 
calls :meth:`Inform.errors_accrued` for the active informer.

If the *reset* argument is True, the error count is reset to 0.


get_prog_name
"""""""""""""

.. py:function:: get_prog_name()
   :noindex:


:func:`get_prog_name` returns the name of the program.
It calls :meth:`Inform.get_prog_name` for the active informer.


get_informer
""""""""""""

.. py:function:: get_informer()
   :noindex:


:func:`get_informer` returns the currently active informer.


set_culprit
"""""""""""

.. py:function:: set_culprit(culprit)
   :noindex:

:func:`set_culprit` saves a culprit in the informer for later use. Any existing 
saved culprit is temporarily moved out of the way.  It calls 
:meth:`Inform.set_culprit` for the active informer.

A culprit is a string, number, or tuple of strings or numbers that would be 
prepended to a message to indicate the object of the message.

:meth:`Inform.set_culprit` is used with Python's *with* statement. The original 
saved culprit is restored when the *with* statement exits.

See :ref:`culprits` for an example of :func:`set_culprit` use.

add_culprit
"""""""""""

.. py:function:: add_culprit(culprit)
   :noindex:

:func:`add_culprit` appends a culprit to any existing saved culprit. It calls 
:meth:`Inform.add_culprit` for the active informer.

A culprit is a string, number, or tuple of strings or numbers that would be 
prepended to a message to indicate the object of the message.

:meth:`Inform.add_culprit` is used with Python's *with* statement. The original 
saved culprit is restored when the *with* statement exits.

See :ref:`culprits` for an example of :func:`add_culprit` use.

get_culprit
"""""""""""

.. py:function:: get_culprit(culprit=None)
   :noindex:

:func:`get_culprit` returns the specified culprit, if any, appended to the end 
of the current culprit that is saved in the informer.  The resulting culprit is 
always returned as a tuple. It calls :meth:`Inform.get_culprit` for the active 
informer.

A culprit is a string, number, or tuple of strings or numbers that would be 
prepended to a message to indicate the object of the message.

See :ref:`culprits` for an example of :func:`get_culprit` use.
