---------------------
Classes and Functions
---------------------


Inform
======

The Inform class controls the active informants.

.. autoclass:: inform.Inform
    :members:

Direct Access Functions
-----------------------

These functions access the currently active informer.

.. autofunction:: inform.done

.. autofunction:: inform.terminate

.. autofunction:: inform.terminate_if_errors

.. autofunction:: inform.errors_accrued

.. autofunction:: inform.get_prog_name

You can also request the active informer:

.. autofunction:: inform.get_informer


InformantFactory
================

.. autoclass:: inform.InformantFactory
    :members:


Inform Utilities
================

.. autofunction:: inform.indent

.. autofunction:: inform.cull

.. autofunction:: inform.is_str

.. autofunction:: inform.is_iterable

.. autofunction:: inform.is_collection

.. autoclass:: inform.Color
    :members:


User Utilities
==============

.. autofunction:: inform.fmt

.. autofunction:: inform.join

.. autofunction:: inform.render

.. autofunction:: inform.os_error

.. autofunction:: inform.conjoin

.. autofunction:: inform.plural

.. autofunction:: inform.full_stop

.. autofunction:: inform.columns


Debug Utilities
===============

.. autofunction:: inform.ddd

.. autofunction:: inform.ppp

.. autofunction:: inform.sss

.. autofunction:: inform.vvv


Predefined Informants
=====================

The following informants are provided. All of the informants except panic and 
debug do not produce any output if *mute* is set.

log
---

.. code-block:: python

   log = InformantFactory(
       output=False,
       log=True,
   )

Saves a message to the log file without displaying it.


comment
-------

.. code-block:: python

   comment = InformantFactory(
       output=lambda informer: informer.verbose and not informer.mute,
       log=True,
       message_color='cyan',
   )

Displays a message only if *verbose* is set. Logs the message. The message is 
displayed in cyan.

Comments are generally used to document unusual occurrences that might warrant 
the user's attention.

codicil
-------

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


narrate
-------

.. code-block:: python

   narrate = InformantFactory(
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
-------

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


output
------

.. code-block:: python

   output = InformantFactory(
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
------

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


debug
-----

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
``ddd()``, ``ppp()``, ``sss()`` and ``vvv()``.


warn
----

.. code-block:: python

   warn = InformantFactory(
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
-----

.. code-block:: python

   error = InformantFactory(
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
-----

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
the message and the header is colored red. The program is terminated with an 
exit status of 1.


panic
-----

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
added to the message and the header is colored red. The program is terminated 
with an exit status of 3.


Exceptions
==========

.. autoexception:: inform.Error
    :members:
