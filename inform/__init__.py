__version__ = '1.0.5'

from .messenger import (
    indent, cull, is_str, is_iterable, is_collection,
    Color, fmt, os_error, conjoin, plural, MessengerGenerator, Messenger,
    log, comment, codicil, narrate, display, output, debug, warn, error, fatal, 
    panic, done, terminate, terminate_if_errors, errors_accrued, Error
)
