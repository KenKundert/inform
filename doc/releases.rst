.. currentmodule:: inform

Releases
========

Latest development release
--------------------------

    | Version: 1.26.3
    | Released: 2022-09-05


1.27 (2022-09-05)
-----------------

- Add markers to :class:`ProgressBar`.


1.26 (2021-09-15)
-----------------

- Added :func:`dedent`.
- Added :class:`LoggingCache`.


1.25 (2021-07-07)
-----------------

- Allow culprits to be falsy.


1.24 (2021-05-18)
-----------------

- Defer evaluation of *stdout* and *stderr*.


1.23 (2020-08-26)
-----------------

- Strip out empty culprits and codicils.


1.22 (2020-08-24)
-----------------

- Added *clone* argument to :class:`InformantFactory`.


1.21 (2020-07-20)
-----------------

- Allow :class:`ProgressBar` output to be suppressed.
- Allow ``/`` to be overridden in :class:`plural`
- Various enhancements to :func:`conjoin` and :func:`full_stop`.
- Added :func:`parse_range` and :func:`format_range` functions.
- Added :func:`title_case` function.


1.20 (2020-01-08)
-----------------

- Add *format* method to :class:`plural`.


1.19 (2019-09-25)
-----------------

- Minor fixes.


1.18 (2019-08-10)
-----------------

- Wrap now applies to codicils passed as arguments.
- Enhance :class:`plural` (now supports pluralizing verbs).
- Add *fmt* argument to :func:`conjoin()`.
- Support *template* attribute on subclasses of :class:`Error`.


1.17 (2019-05-16)
-----------------

- Added :func:`is_mapping()`


1.16 (2019-04-27)
-----------------

- Add end support to :func:`join()`.
- Allow previous logfile to be saved.
- Allow urgency to be specified on notifications.
- Allow :func:`render()` support in user-defined classes with addition of special methods.


1.15 (2019-01-16)
-----------------

- Added *error_status* argument to :class:`Inform`.
- Enhanced :class:`plural`.  This enhancement is not backward 
    compatible.
- Enhance for :func:`render()` to allow it to be used in a __repr__ function.


1.14 (2018-12-03)
-----------------

- Added :func:`render_bar` utility function.
- Added :class:`ProgressBar` class.
- Added :class:`Info` class.
- Added :meth:`Inform.join_culprit` method and 
    :func:`join_culprit`.
- Allow culprit to be passed into :meth:`Error.report()` and 
    :meth:`Error.terminate()`.
- Added :meth:`Error.reraise` method.
- Allow a codicil or codicils to be added to any informant.
- Added *codicil* named argument to informants and :class:`Error`.
- Added *informant* named argument to :class:`Error`.
- Use colorscheme of active informer as default for colorizers.
- :meth:`Error.get_culprit` now returns a tuple rather than a string.
- Added :meth:`Error.join_culprit`.
- Added :meth:`Error.get_codicil`.


1.13 (2018-08-11)
-----------------

- Added :func:`aaa()` debug function.
- Added exit argument to :func:`done()`, :func:`terminate()`, 
    and :func:`terminate_if_errors()`.
- :func:`terminate()` now produces an exit status of 0 if there was 
    no errors reported.
- Added :func:`set_culprit()`, :func:`add_culprit()`
    and :func:`get_culprit()`.


1.12 (2018-02-18)
-----------------

- do not use notify override on continuations.
- tidied up a bit.


1.11 (2017-12-25)
-----------------

- Released the documentation.
- Added ability to override template in :class:`Error`.
- Added *stream_policy* option.
- Added *notify_if_no_tty* option.
- Informers now stack, so disconnecting from an existing informer reinstates 
    the previous informer.
- Generalize :func:`cull()`.
- Add support for multiple templates.
- Added :func:`join()` function.
