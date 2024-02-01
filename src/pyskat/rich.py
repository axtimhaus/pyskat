import click
from rich import get_console
from rich.traceback import install

console = get_console()

SUPPRESS_TRACEBACKS = [
    click
]

install(
    console=console,
    show_locals=False,
    suppress=SUPPRESS_TRACEBACKS
)
