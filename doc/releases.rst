Releases
========

**Latest development release**:
    | Version: 1.18.1
    | Released: 2019-08-22

**1.19 (2019-09-25)**:
    - Minor fixes.

**1.18 (2019-08-10)**:
    - Wrap now applies to codicils passed as arguments.
    - Enhance :class:`inform.plural` (now supports pluralizing verbs).
    - Add *fmt* argument to :func:`inform.conjoin()`.
    - Support *template* attribute on subclasses of :class:`inform.Error`.

**1.17 (2019-05-16)**:
    - Added :func:`inform.is_mapping()`

**1.16 (2019-04-27)**:
    - Add end support to :func:`inform.join()`.
    - Allow previous logfile to be saved.
    - Allow urgency to be specified on notifications.
    - Allow :func:`inform.render()` support in user-defined classes with addition of special methods.

**1.15 (2019-01-16)**:
    - Added *error_status* argument to :class:`inform.Inform`.
    - Enhanced :class:`inform.plural`.  This enhancement is not backward 
      compatible.
    - Enhance for :func:`inform.render()` to allow it to be used in a __repr__ function.

**1.14 (2018-12-03)**:
    - Added :func:`inform.render_bar` utility function.
    - Added :class:`inform.ProgressBar` class.
    - Added :class:`inform.Info` class.
    - Added :meth:`inform.Inform.join_culprit` method and 
      :func:`inform.join_culprit`.
    - Allow culprit to be passed into :meth:`inform.Error.report()` and 
      :meth:`inform.Error.terminate()`.
    - Added :meth:`inform.Error.reraise` method.
    - Allow a codicil or codicils to be added to any informant.
    - Added *codicil* named argument to informants and :class:`inform.Error`.
    - Added *informant* named argument to :class:`inform.Error`.
    - Use colorscheme of active informer as default for colorizers.
    - :meth:`inform.Error.get_culprit` now returns a tuple rather than a string.
    - Added :meth:`inform.Error.join_culprit`.
    - Added :meth:`inform.Error.get_codicil`.

**1.13 (2018-08-11)**:
    - Added :func:`inform.aaa()` debug function.
    - Added exit argument to :func:`inform.done()`, :func:`inform.terminate()`, 
      and :func:`inform.terminate_if_errors()`.
    - :func:`inform.terminate()` now produces an exit status of 0 if there was 
      no errors reported.
    - Added :func:`inform.set_culprit()`, :func:`inform.add_culprit()`
      and :func:`inform.get_culprit()`.

**1.12 (2018-02-18)**:
    - do not use notify override on continuations.
    - tidied up a bit.

**1.11 (2017-12-25)**:
    - Released the documentation.
    - Added ability to override template in :class:`inform.Error`.
    - Added *stream_policy* option.
    - Added *notify_if_no_tty* option.
    - Informers now stack, so disconnecting from an existing informer reinstates 
      the previous informer.
    - Generalize :func:`inform.cull()`.
    - Add support for multiple templates.
    - Added :func:`inform.join()` function.
