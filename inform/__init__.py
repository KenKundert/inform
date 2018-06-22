__version__ = '1.12.5'
__released__ = '2018-06-21'

from .inform import (
    # inform utility functions
    indent, cull, is_str, is_iterable, is_collection, join,

    # user utility functions
    Color, fmt, render, os_error, conjoin, plural, full_stop, columns,

    # debug functions
    aaa, ppp, ddd, vvv, sss,

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
