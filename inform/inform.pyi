from typing import Any, Callable, Iterable, Mapping, Sequence, TextIO
from pathlib import Path

__released__: str
__version__: str

def indent(
    text: str,
    leader: str = ...,
    first: int = ...,
    stops: int = ...,
    sep: str = ...
) -> str:
    ...

def cull(
        collection: Sequence,
        **kwargs
) -> Sequence:
    ...

def is_str(arg: Any) -> bool: ...
def is_iterable(obj: Any) -> bool: ...
def is_collection(obj: Any) -> bool: ...
def is_mapping(obj: Any) -> bool: ...
def is_array(obj: Any) -> bool: ...

class Color:
    enable: bool

    def __init__(
        self,
        color: str,
        *,
        scheme: str = ...,
        enable: bool = ...
    ) -> None:
        ...

    def __call__(self, *args, **kwargs) -> str: ...

    @staticmethod
    def isTTY(stream=TextIO) -> bool: ...

    @classmethod
    def strip_colors(
        cls,
        text: str
    ) -> str: ...

class LoggingCache:
    pass

def join(*args, **kwargs) -> str: ...

def render(
    obj: Any,
    sort: bool = ...,
    level: int = ...,
    tab: str = ...
) -> str:
    ...

def fmt(message: str, *args, **kwargs) -> str: ...

def dedent(
    text: str,
    strip_nl: str = ...,
    *,
    bolm: str = ...,
    wrap: bool = ...
) -> str:
    ...

def os_error(e: OSError) -> str: ...

def conjoin(
    iterable,
    conj: str = ...,
    sep: str = ...,
    end: str = ...,
    fmt: str = ...
) -> str:
    ...

def title_case(
    s: str,
    exceptions: Sequence[str] =...
) -> str:
    ...

def did_you_mean(
    invalid_str: str,
    valid_strs: Sequence[str]
) -> str:
    ...

def parse_range(
    items_str: str,
    cast: Callable = ...,
    range: Callable = ...,
    block_delim: str = ...,
    range_delim: str = ...,
) -> set:
    ...

def format_range(
    items: Iterable,
    diff: Callable = ...,
    key: Callable | None = ...,
    str: Callable = ...,
    block_delim: str = ...,
    range_delim: str = ...,
) -> str:
    ...

class plural:
    def __init__(
        self,
        value: int | Sequence,
        *,
        num: str = ...,
        invert: str = ...,
        slash: str = ...
    ) -> None:
        ...

    def format(self, formatter: str) -> str: ...

    def __format__(self, formatter: str) -> str: ...

    def __int__(self) -> int: ...

class truth:
    def __init__(
        self,
        value: bool,
        *,
        interpolate: str = ...,
        slash: str = ...
    ) -> None:
        ...

    def format(self, formatter: str) -> str: ...

    def __format__(self, formatter: str) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...

def full_stop(
    sentence: str | Exception,
    end: str = ...,
    allow: str = ...
) -> str:
    ...

def columns(
    array: Sequence[str],
    pagewidth: int = ...,
    alignment: str = ...,
    leader: str = ...,
    min_sep_width: int = ...,
    min_col_width: int = ...,
):
    ...

def render_bar(
    value: float,
    width: int = ...,
    full_width: bool = ...
):
    ...

class Info:
    def __init__(self, **kwargs) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def get(self, name: str, default: Any = ...) -> Any: ...
    def render(self, template: str) -> str: ...

class ProgressBar:
    def __init__(
        self,
        stop: float | Iterable,
        start: float = ...,
        *,
        log: bool = ...,
        prefix: str = ...,
        width: int = ...,
        informant: InformantFactory = ...,
        markers: Mapping[str, tuple[str, str | Color | None]] = ...,
    ) -> None:
        ...

    def draw(
        self,
        abscissa: float,
        marker: str = ...,
    ) -> None:
        ...

    def done(self) -> None: ...

    def escape(self) -> None: ...

    def __enter__(self): ...
    def __exit__(self, exception, value, traceback) -> None: ...
    def __iter__(self): ...

def tree(data: Any, squeeze: bool) -> str: ...

def ppp(*args, **kwargs) -> None: ...
def ddd(*args, **kwargs): ...
def vvv(*args) -> None: ...
def aaa(*args, **kwargs) -> Any: ...
def ccc(*args, **kwargs) -> None: ...
def sss() -> None: ...

class InformantFactory:
    severity: str
    is_error: bool
    log: bool
    output: bool
    notify: bool
    terminate: bool
    is_continuation: bool
    message_color: Color
    header_color: Color
    stream: TextIO
    def __init__(self, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs) -> None: ...

log: InformantFactory
comment: InformantFactory
codicil: InformantFactory
narrate: InformantFactory
display: InformantFactory
output: InformantFactory
notify: InformantFactory
debug: InformantFactory
warn: InformantFactory
error: InformantFactory
fatal: InformantFactory
panic: InformantFactory

class Inform:

    def __init__(
        self,
        mute: bool = ...,
        quiet: bool = ...,
        verbose: bool = ...,
        narrate: bool = ...,
        logfile: str | Path | TextIO | bool = ...,
        prev_logfile_suffix: str = ...,
        error_status: int = ...,
        prog_name: bool | str = ...,
        argv: Sequence[str] = ...,
        version: str = ...,
        termination_callback: Callable = ...,
        colorscheme: str | None = ...,
        flush: bool = ...,
        stdout: TextIO = ...,
        stderr: TextIO = ...,
        length_thresh: int = ...,
        culprit_sep: str = ...,
        stream_policy: str | Callable = ...,
        notify_if_no_tty: bool = ...,
        notifier: str =...,
        **kwargs,
    ) -> None:
        ...

    def __getattr__(self, name: str) -> Any: ...

    @property
    def stdout(self) -> TextIO: ...

    @property
    def stderr(self) -> TextIO: ...

    def suppress_output(self, mute: bool = ...) -> None: ...

    def set_logfile(
        self,
        logfile: str | Path | TextIO | bool,
        prev_logfile_suffix: str = ...,
        encoding: str = ...,
    ) -> None:
        ...

    def flush_logfile(self) -> None: ...

    def close_logfile(self, status: str | int = ...) -> None: ...

    def set_stream_policy(self, stream_policy: str | Callable) -> None: ...

    def done(self, exit: bool = ...): ...

    def terminate(
        self,
        status: int | bool | str | None = ...,
        exit: bool = ...,
    ) -> int: ...

    def terminate_if_errors(
        self,
        status: int | bool | str | None = ...,
        exit: bool = ...,
    ) -> int:
        ...

    def errors_accrued(self, reset: bool = ...) -> int: ...

    def get_prog_name(self) -> str: ...

    def disconnect(self) -> None: ...

    class CulpritContextManager:
        def __init__(
            self,
            informer: InformantFactory,
            culprit: Any,
            append: bool = ...,
        ) -> None: ...

    def set_culprit(
        self,
        culprit: Any,
    ):
        ...

    def add_culprit(
        self,
        culprit: Any,
    ):
        ...

    def get_culprit(
        self,
        culprit: Any,
    ) -> Any:
        ...

    def join_culprit(
        self,
        culprit: Any,
    ) -> Any:
        ...

    def __enter__(self): ...
    def __exit__(self, exception, value, traceback) -> None: ...

def done(exit: bool = ...) -> int: ...

def terminate(
    status: int | bool | str | None = ...,
    exit: bool = ...,
) -> int:
    ...

def terminate_if_errors(
    status: int | bool | str | None = ...,
    exit: bool = ...,
) -> int:
    ...

def errors_accrued(reset: bool = ...) -> int: ...

def get_prog_name() -> str: ...

def get_informer() -> Inform: ...

def set_informer(new: Inform): ...

def set_culprit(culprit: Any): ...

def add_culprit(culprit: Any): ...

def get_culprit(culprit: Any = ...) -> Any: ...

def join_culprit(culprit: Any = ...) -> str: ...

class Error(Exception):
    args: tuple
    kwargs: dict

    def __init__(self, *args, **kwargs) -> None: ...

    def get_message(self, template: str = ...) -> str: ...

    def get_culprit(self, culprit: Any = ...) -> Any: ...

    def get_codicil(self, codicil: Any = ...) -> tuple: ...

    def report(self, **new_kwargs) -> None: ...

    def terminate(self, **new_kwargs) -> None: ...

    def reraise(self, **new_kwargs) -> None: ...

    def render(self, template: str = ...) -> str: ...

    def __getattr__(self, name: str): ...
