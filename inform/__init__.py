__version__ = '1.12.0'
__released__ = '2018-02-18'

from .inform import (
    # inform utility functions
    indent, cull, is_str, is_iterable, is_collection, join,

    # user utility functions
    Color, fmt, render, os_error, conjoin, plural, full_stop, columns,

    # debug functions
    ppp, ddd, vvv, sss,

    # inform classes
    InformantFactory, Inform, Error,

    # inform functions
    done, terminate, terminate_if_errors, errors_accrued, get_prog_name,

    # built-in informants
    log, comment, codicil, narrate, display, output,
    notify, debug, warn, error, fatal, panic,

    # the currently active informer
    get_informer
)
