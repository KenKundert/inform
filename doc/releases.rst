Releases
========

**1.11 (2017-12-25)**:
    | Version: 1.11.0
    | Released: 2017-12-25

    - Released the documentation.
    - Added ability to override template in :class:`inform.Error`.
    - Added *stream_policy* option.
    - Added *notify_if_no_tty* option.
    - Informers now stack, so disconnecting from an existing informer reinstates 
      the previous informer.
    - Generallize cull.
    - Add support for multiple templates.
    - Add *join* function.
