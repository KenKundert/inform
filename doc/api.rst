.. currentmodule:: inform

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

.. autofunction:: inform.set_culprit

.. autofunction:: inform.add_culprit

.. autofunction:: inform.get_culprit

You can also request the active informer:

.. autofunction:: inform.get_informer


InformantFactory
================

.. autoclass:: inform.InformantFactory
    :members:


Inform Utilities
================

.. autoclass:: inform.Color
    :members:

.. autoclass:: inform.LoggingCache

.. autofunction:: inform.cull

.. autofunction:: inform.indent

.. autofunction:: inform.is_collection

.. autofunction:: inform.is_iterable

.. autofunction:: inform.is_array

.. autofunction:: inform.is_mapping

.. autofunction:: inform.is_str


User Utilities
==============

.. autoclass:: inform.Info
    :members:

.. autoclass:: inform.ProgressBar
    :members:

.. autoclass:: inform.bar
    :members:

.. autofunction:: inform.columns

.. autofunction:: inform.conjoin

.. autofunction:: inform.dedent

.. autofunction:: inform.did_you_mean

.. autofunction:: inform.fmt

.. autofunction:: inform.format_range

.. autofunction:: inform.full_stop

.. autofunction:: inform.join

.. autofunction:: inform.parse_range

.. autofunction:: inform.os_error

.. autoclass:: inform.plural
    :members:

.. autoclass:: inform.truth
    :members:

.. autofunction:: inform.render

.. autofunction:: inform.render_bar

.. autofunction:: inform.title_case


Debug Utilities
===============

.. autofunction:: inform.aaa

.. autofunction:: inform.ccc

.. autofunction:: inform.ddd

.. autofunction:: inform.ppp

.. autofunction:: inform.sss

.. autofunction:: inform.vvv


Exceptions
==========

.. autoexception:: inform.Error
    :members:
