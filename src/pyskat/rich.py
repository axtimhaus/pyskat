import click
import pandas as pd
from rich import get_console
from rich.traceback import install
from rich.table import Table

console = get_console()

SUPPRESS_TRACEBACKS = [
    click
]

install(
    console=console,
    show_locals=False,
    suppress=SUPPRESS_TRACEBACKS
)


def print_pandas_dataframe(df: pd.DataFrame):
    table = Table()

    for col in df.index.names:
        table.add_column(col, header_style="italic")

    for col in df.columns:
        table.add_column(col)

    for row in df.itertuples():
        index = (str(e) for e in row[0]) if isinstance(row[0], tuple) else (str(row[0]),)
        data = (str(e) for e in row[1:])
        table.add_row(*index, *data)

    console.print(table)
