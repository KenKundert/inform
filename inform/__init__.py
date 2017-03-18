__version__ = '1.7.0'
__released__ = '2017-03-17'

from .inform import (
    # inform utilities
    indent, cull, is_str, is_iterable, is_collection,

    # user utilities
    Color, fmt, render, os_error, conjoin, plural, full_stop,

    # inform classes
    InformantGenerator, Inform, Error,

    # inform functions
    done, terminate, terminate_if_errors, errors_accrued,

    # built-in informants
    log, comment, codicil, narrate, display, output,
    notify, debug, warn, error, fatal, panic,
)
