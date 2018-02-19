Releases
========

**1.11 (2017-12-25)**:
    | Released: 2018-02-18

    - Released the documentation.
    - Added ability to override template in :class:`inform.Error`.
    - Added *stream_policy* option.
    - Added *notify_if_no_tty* option.
    - Informers now stack, so disconnecting from an existing informer reinstates 
      the previous informer.
    - Generalize cull.
    - Add support for multiple templates.
    - Add *join* function.

**1.12 (2018-02-18)**:
    | Version: 1.12.0

    - do not use notify override on continuations.
    - tidied up a bit.
