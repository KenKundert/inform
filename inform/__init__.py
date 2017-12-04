__version__ = '1.10.1'
__released__ = '2017-12-03'

from .inform import (
    # inform utilities
    indent, cull, is_str, is_iterable, is_collection,

    # user utilities
    Color, fmt, render, os_error, conjoin, plural, full_stop, columns,
    ppp, ddd, vvv, sss,

    # inform classes
    InformantFactory, Inform, Error,

    # inform functions
    done, terminate, terminate_if_errors, errors_accrued, get_prog_name,

    # built-in informants
    log, comment, codicil, narrate, display, output,
    notify, debug, warn, error, fatal, panic,
)
