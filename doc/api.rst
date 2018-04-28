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

Several of the above methods are also available as stand-alone functions that
act on the currently active informer.  This make it easy to use their
functionality even if you do not have local access to the informer.

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

.. autofunction:: inform.aaa

.. autofunction:: inform.ddd

.. autofunction:: inform.ppp

.. autofunction:: inform.sss

.. autofunction:: inform.vvv


Exceptions
==========

.. autoexception:: inform.Error
    :members:
