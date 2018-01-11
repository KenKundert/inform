Releases
========

**1.11 (2017-12-25)**:
    | Version: 1.11.3
    | Released: 2018-01-11

    - Released the documentation.
    - Added ability to override template in :class:`inform.Error`.
    - Added *stream_policy* option.
    - Added *notify_if_no_tty* option.
    - Informers now stack, so disconnecting from an existing informer reinstates 
      the previous informer.
    - Generallize cull.
    - Add support for multiple templates.
    - Add *join* function.
