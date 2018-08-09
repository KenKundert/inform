.. Initialize Inform and suppress outputting of program name

    >>> from inform import Inform
    >>> inform = Inform(prog_name=False)


User's Guide
============

.. _using informants:

Using Informants
----------------

This package defines a collection of 'print' functions that are referred to as 
informants.  They include include :ref:`log`, :ref:`comment`, :ref:`codicil`, 
:ref:`narrate`, :ref:`display`, :ref:`output`, :ref:`notify`, :ref:`debug`, 
:ref:`warn`, :ref:`error`, :ref:`fatal` and :ref:`panic`.

They all take arguments in a manner that is a generalization of Python's 
built-in print function.  Each of the informants is used for a specific purpose, 
but they all take and process arguments in the same manner.  These functions 
will be distinguished in the :ref:`predefined informants` section.  In this 
section, the manner in which they process their arguments is presented.

With the simplest use of the program, you simply import the informants you need 
and call them, placing those things that you wish to print in the argument list 
as unnamed arguments:

.. code-block:: python

    >>> from inform import display
    >>> display('ice', 9)
    ice 9

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
   number or a tuple that contains strings and numbers. If *culprit* is a tuple, 
   the members are converted to strings and joined with *culprit_sep* (default 
   is ', ').

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

*culprit* is used to identify the target of the message. If the message is 
pointing out a problem the *culprit* is generally the source of the problem.

Here is an example that demonstrates the wrap and composite culprit features:

..  code-block:: python

   >>> from inform import error

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
in you informer using :func:`inform.set_culprit` or :func:`inform.add_culprit` 
and then recall them when needed using :func:`inform.get_culprit`.  For example:

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

The *template* strings are the same as one would use with Python's built-in 
format function and string method (as described in `Format String Syntax 
<https://docs.python.org/3/library/string.html#format-string-syntax>`_.  The 
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
    ...     display(name, code, desc, template=('{:>5s} = {}  -- {}', '{:>5s} = {}'))
     blue = 3346ff
    green = 4fff33  -- success
      red = ff5733  -- failure

    >>> for name in sorted(colors.keys()):
    ...     code, desc = colors[name]
    ...     display(k=name, v=code, d=desc, template=('{k:>5s} = {v}  -- {d}', '{k:>5s} = {v}'))
     blue = 3346ff
    green = 4fff33  -- success
      red = ff5733  -- failure

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
informants using :class:`inform.InformantFactory`.

All of the informants except :ref:`panic` and :ref:`debug` do not produce any 
output if *mute* is set.

If you do not care for the default behavior for the predefined informants, you 
can customize them by overriding their attributes. For example, in many cases 
you might prefer that normal program output is not logged, either because it is 
voluminous or because it is sensitive. In that case you can simple override the 
*log* attributes for the *display* and *output* informants like so:

.. code-block:: python

   from inform import display, output
   display.log = False
   output.log = False


.. _log:

log
"""

.. code-block:: python

   log = InformantFactory(
       output=False,
       log=True,
   )

Saves a message to the log file without displaying it.


.. _comment:

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


.. _codicil:

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


.. _narrate:

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


.. _display:

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


.. _output:

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
    >>> output('We the people ...')
    We the people ...


.. _notify:

notify
""""""

.. code-block:: python

   notify = InformantFactory(
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


.. _debug:

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

The *debug* informant is being deprecated in favor of the debugging functions 
``aaa()``, ``ddd()``, ``ppp()``, ``sss()`` and ``vvv()``.


.. _warn:

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


.. _error:

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
the message. The the header is colored red when writing to the console.

.. code-block:: python

    >>> from inform import Inform, error
    >>> informer = Inform(prog_name="myprog")
    >>> error('invalid value specified, expected a number.', culprit='count')
    myprog error: count: invalid value specified, expected a number.


.. _fatal:

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


.. _panic:

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



.. informers:

Informant Control
-----------------

For more control of the informants, you can import and instantiate the 
:class:`inform.Inform` class along with the desired informants.  This gives you 
the ability to specify options:

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

    >>> str(logfile_text[:10]), str(logfile_text[-13:])
    ('Invoked as', 'running test\n')


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

You can create your own informants using :class:`inform.InformantFactory`. One 
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
:class:`inform.Inform`.  In this case *Inform* simply saves the value and makes 
it available as an attribute, and it is this attribute that is queried by the 
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


.. _exceptions:

Exceptions
----------

An exception, :class:`inform.Error`, is provided that takes the same arguments 
as an informant.  This allows you to catch the exception and handle it if you 
like.  Any arguments you pass into the exception are retained and are available 
when processing the exception.  The exception provides the *report* and 
*terminate* methods that processes the exception as an error or fatal error if 
you find that you can do nothing else with the exception:

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
message and the culprit. You can also cast the exception to a string or call the 
:meth:`inform.Error.render` method to get a string that contains both the 
message and the culprit formatted so that it can be shown to the user.

All positional arguments are available in *e.args* and any keyword arguments 
provided are available in *e.kwargs*.

One common approach to using *Error* is to pass all the arguments that make up 
the error message as arguments and then assemble them into the message by 
providing a template.  In that way the arguments are directly available to the 
handler if needed. For example:

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

You can override the template by passing a new one to :meth:`get_message`, 
:meth:`render`, :meth:`report`, or :meth:`terminate`. This can be helpful if you 
need to translate a message or change it to make it more meaningful to the end 
user:

.. code-block:: python

    >>> try:
    ...     raise Error(name, template="name '{}' is not defined.")
    ... except Error as e:
    ...     e.report("'{}' ist nicht definiert.")
    myprog error: 'alfa' ist nicht definiert.


Utilities
---------

Several utility functions are provided for your convenience. They are often 
helpful when creating messages.


.. _color desc:

Color Class
"""""""""""

The :class:`inform.Color` class creates colorizers, which are functions used to 
render text in a particular color.  They are like the Python print function in 
that they take any number of unnamed arguments that are converted to strings and 
then joined into a single string. The string is then coded for the chosen color 
and returned. For example:

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
schemes: *None*, 'light', and 'dark'. With *None* the text is not colored. In 
general it is best to use the 'light' colorscheme on 'dark' backgrounds and the 
'dark' colorscheme on light backgrounds.

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
example uses the :meth:`inform.Color.isTTY` method to determine whether the 
output stream, the standard output by default, is a console.

.. code-block:: python

   >> warning = Color('yellow', enable=Color.isTTY())
   >> warning('Cannot find precursor, ignoring.')
   Cannot find precursor, ignoring.



.. _columns desc:

columns
"""""""

.. py:function:: columns(array, pagewidth=79, alignment='<', leader='    ')

:func:`inform.columns` distributes the values of an array over enough columns to 
fill the screen.

This example uses prints out the phonetic alphabet:

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

.. py:function:: conjoin(iterable, conj=' and ', sep=', ')

:func:`inform.conjoin` is like ''.join(), but allows you to specify 
a conjunction that is placed between the last two elements. For example:

.. code-block:: python

    >>> from inform import conjoin
    >>> conjoin(['a', 'b', 'c'])
    'a, b and c'

    >>> conjoin(['a', 'b', 'c'], conj=' or ')
    'a, b or c'


.. _cull desc:

cull
""""

.. py:function:: cull(collection, [remove])

:func:`inform.cull` strips items from a collection that have a particular value.  
The collection may be list-like (*list*, *tuple*, *set*, etc.) or 
a dictionary-like (*dict*, *OrderedDict*).  A new collection of the same type is 
returned with the undesirable values removed.

By default, :func:`inform.cull` strips values that would be *False* when cast to 
a Boolean (0, *False*, *None*, '', (), [], etc.).  A particular value may be 
specified using the *remove* as a keyword argument.  The value of remove may be 
a collection, in which case any value in the collection is removed, or it may be 
a function, in which case it takes a single item as an argument and returns 
*True* if that item should be removed from the list.

.. code-block:: python

    >>> from inform import cull, display
    >>> display(*cull(['a', 'b', None, 'd']), sep=', ')
    a, b, d

    >>> accounts = dict(checking=1100.16, savings=13948.78, brokerage=0)
    >>> for name, amount in sorted(cull(accounts).items()):
    ...     display(name, amount, template='{:>10s}: ${:,.2f}')
      checking: $1,100.16
       savings: $13,948.78


.. _fmt desc:

fmt
"""

.. py:function:: fmt(msg, \*args, \**kwargs)

:func:`inform.fmt` is similar to ''.format(), but it can pull arguments from the 
local scope.

.. code-block:: python

    >>> from inform import conjoin, display, fmt, plural

    >>> filenames = ['a', 'b', 'c', 'd']
    >>> filetype = 'CSV'
    >>> display(
    ...     fmt(
    ...         'Reading {filetype} {files}: {names}.',
    ...         files=plural(filenames, 'file'),
    ...         names=conjoin(filenames),
    ...     )
    ... )
    Reading CSV files: a, b, c and d.

Notice that *filetype* was not explicitly passed into *fmt()* even though it was 
explicitly called out in the format string.  *filetype* can be left out of the 
argument list because if *fmt* does not find a named argument in its argument 
list, it will look for a variable of the same name in the local scope.


.. _full_stop desc:

full_stop
"""""""""

.. py:function:: full_stop(string)

:func:`inform.full_stop` adds a period to the end of the string if needed (if 
the last character is not a period, question mark or exclamation mark). It 
applies str() to its argument, so it is generally a suitable replacement for str 
in str(exception) when trying extract an error message from an exception.

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

:func:`inform.indent` indents *text*. Multiples of *leader* are added to the 
beginning of the lines to indent.  *first* is the number of indentations used 
for the first line relative to the others (may be negative but (first + stops) 
should not be.  *stops* is the default number of indentations to use. *sep* is 
the string used to separate the lines.

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


.. _is_collection desc:

is_collection
"""""""""""""

.. py:function:: is_collection(obj)

:func:`inform.is_collection` returns *True* if its argument is a collection.  
This includes objects such as lists, sets, dictionaries, etc.  It does not 
include strings.

.. code-block:: python

    >>> from inform import is_collection

    >>> is_collection('abc')
    False

    >>> is_collection(['a', 'b', 'c'])
    True


.. _is_iterable desc:

is_iterable
"""""""""""

.. py:function:: is_iterable(obj)

:func:`inform.is_iterable` returns *True* if its argument is a collection or 
a string.

.. code-block:: python

    >>> from inform import is_iterable

    >>> is_iterable('abc')
    True

    >>> is_iterable(['a', 'b', 'c'])
    True


.. _is_str desc:

is_str
""""""

.. py:function:: is_str(obj)

:func:`inform.is_str` returns *True* if its argument is a string-like object.

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

:func:`inform.join` combines the arguments in a manner very similar to an 
:ref:`informant <using informants>` and returns the result as a string.  Uses 
the *sep*, *template* and *wrap* keyword arguments to combine the arguments.


.. code-block:: python

    >>> from inform import display, join

    >>> accounts = dict(checking=1100.16, savings=13948.78, brokerage=0)
    >>> lines = []
    >>> for name, amount in accounts.items():
    ...     lines.append(join(name, amount, template='{:>10s}: ${:,.2f}'))

    display(lines, sep='\n')
     brokerage: $0.00
      checking: $1,100.16
       savings: $13,948.78


.. _os_error desc:

os_error
""""""""

.. py:function:: os_error(exception)

:func:`inform.os_error` generates clean messages for operating system errors.

.. code-block:: python

    >>> from inform import error, os_error

    >>> try:
    ...     with open('config') as f:
    ...         contents = f.read()
    ... except (OSError, IOError) as e:
    ...     error(os_error(e))
    myprog error: config: no such file or directory.


.. _plural desc:

plural
""""""

.. py:function:: plural(count, singular_form, plural_form=*None*)

Produces either the singular or plural form of a word based on a count.
The count may be an integer, or an iterable, in which case its length is used. 
If the plural form is not given, the singular form is used with an 's' added to 
the end.

.. code-block:: python

    >>> from inform import conjoin, display, plural

    >>> filenames = ['a', 'b', 'c', 'd']
    >>> display(
    ...     files=plural(filenames, 'file'), names=conjoin(filenames),
    ...     template='Reading {files}: {names}.'
    ... )
    Reading files: a, b, c and d.


.. _render desc:

render
""""""

.. py:function:: render(obj, sort=None, level=0, tab='    ')

:func:`inform.render` recursively converts an object to a string with reasonable 
formatting.  Has built in support for the base Python types (*None*, *bool*, 
*int*, *float*, *str*, *set*, *tuple*, *list*, and *dict*).  If you confine 
yourself to these types, the output of :func:`inform.render` can be read by the 
Python interpreter. Other types are converted to string with *repr()*. The 
dictionary keys and set values are sorted if sort is *True*. Sometimes this is 
not possible because the values are not comparable, in which case render reverts 
to the natural order.

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

:func:`inform.aaa` prints and then returns its argument.  The argument may be 
name or unnamed.  If named, the name is used as a label when printing the value 
of the argument.  It can be used to print the value of a term within an 
expression without being forced to replicate that term.

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
    myprog DEBUG: <doctest user.rst[135]>, 2, __main__: int1: 2
    myprog DEBUG: <doctest user.rst[135]>, 2, __main__: int2: 2
    vout = 1.4
    myprog DEBUG: <doctest user.rst[135]>, 2, __main__: int1: 1.6
    myprog DEBUG: <doctest user.rst[135]>, 2, __main__: int2: 3.6
    vout = 2.52


.. _ddd desc:

ddd
"""

.. py:function:: ddd(\*args, \*\*kwargs)

:func:`inform.ddd` pretty prints all of both its unnamed and named arguments.

.. code:: python

    >>> from inform import ddd
    >>> a = 1
    >>> b = 'this is a test'
    >>> c = (2, 3)
    >>> d = {'a': a, 'b': b, 'c': c}
    >>> ddd(a, b, c, d)
    myprog DEBUG: <doctest user.rst[141]>, 1, __main__:
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
    myprog DEBUG: <doctest user.rst[143]>, 1, __main__:
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
    myprog DEBUG: <doctest user.rst[145]>, 4, __main__.Info.__init__():
        self = Info object containing {
            'email': 'ted@ledbelly.com',
            'name': 'Ted Ledbelly',
        }


.. _ppp desc:

ppp
"""

.. py:function:: ppp(\*args, \*\*kwargs)

:func:`inform.ppp` is very similar to the normal Python print function in that 
it prints out the values of the unnamed arguments under the control of the named 
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
    myprog DEBUG: <doctest user.rst[152]>, 1, __main__: 1 this is a test (2, 3)


.. _sss desc:

sss
"""

.. py:function:: sss()

:func:`inform.sss` prints a stack trace, which can answer the *How did I get 
here?* question better than a simple print function.

    .. code:: python

        >> from inform import sss

        >> def foo():
        ..     sss()
        ..     print('CONTINUING')

        >> foo()
        DEBUG: <doctest user.rst[142]>:2, __main__.foo():
            Traceback (most recent call last):
                ...
        CONTINUING


.. _vvv desc:

vvv
"""

.. py:function:: vvv(\*args)

:func:`inform.vvv` prints variables from the calling scope. If no arguments are 
given, then all the variables are printed. You can optionally give specific 
variables on the argument list and only those variables are printed.

.. code:: python

    >>> from inform import vvv

    >>> vvv(b, d)
    myprog DEBUG: <doctest user.rst[154]>, 1, __main__:
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
    myprog DEBUG: <doctest user.rst[157]>, 1, __main__:
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

    from inform import aaa, ddd, ppp, sss, vvv
    builtins.aaa = aaa
    builtins.ddd = ddd
    builtins.ppp = ppp
    builtins.sss = sss
    builtins.vvv = vvv

