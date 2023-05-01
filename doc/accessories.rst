.. currentmodule:: inform

.. _inform_accessories:

Accessories
===========

.. _ntlog accessory:

Logging with ntLog
------------------

`ntLog <https://github.com/KenKundert/ntlog>`_ is a log file aggregation 
utility.

Unlike daemons, *Inform* based applications tend to run on demand.  If it 
generates a log file, each run over-writes over a previously generated logfile.  
This can be problematic if you are interested in keeping a log of events that do 
not occur during each run.

*ntlog* is a utility that accumulates logfiles into `NestedText 
<https://nestedtext.org>`_ file.  It provides *NTlog*, a class whose instances 
provide a output file stream interface.  They can be specified to 
:class:`Inform` as the *logfile*, and in doing so, provide an accumulating 
logfile.  *NTlog* allows you to specify trimming parameters to keep the logfile 
from getting too big.

Here are two examples that use *ntlog* with *inform*.  The first is used with 
a short-lived processes:

.. code-block:: python

    from ntlog import NTlog
    from inform import Inform, display, error, log

    with (
        NTlog('appname.log.nt', keep_for='7d') as ntlog,
        Inform(logfile=ntlog) as inform,
    ):
        display('status message')
        log('log message')
        if there_is_a_problem:
            error('error message')
        ...

The next example demonstrates how to use *ntlog* with long-lived processes.  The 
difference from the above example is that *ntlog* is configured to create 
a temporary log file and *Inform* is configured to flush after each write.  The 
temporary logfile is intended to allow you to monitor the progress of the 
process as it runs.

.. code-block:: python

    with (
        NTlog('appname.log.nt', 'appname.log', keep_for='7d') as ntlog,
        Inform(logfile=ntlog, flush=True) as inform,
    ):
        display('status message')
        log('log message')
        if there_is_a_problem:
            error('error message')
        ...
