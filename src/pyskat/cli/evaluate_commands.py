from pathlib import Path
import click
import numpy as np
import pandas as pd

from .series_commands import series_id_argument, CurrentSeries, pass_current_series
from ..backend import Backend
from .. import plugins
from ..rich import console, print_pandas_dataframe
from .main import pass_backend


@click.group()
def evaluate():
    """Evaluate and display game results per series and in total."""


@evaluate.command()
@click.option(
    "-s",
    "--sort-by",
    type=click.STRING,
    default="score",
    help="Column key to sort results by.",
)
@click.option(
    "-r",
    "--reverse",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help="Sort in reverse order.",
)
@pass_backend
def show(backend: Backend, sort_by: str | None, reverse: bool):
    """Evaluate and display game results per series and in total."""
    try:
        evaluation = plugins.evaluate_results(backend, None)
        evaluation_total = plugins.evaluate_results_total(backend, evaluation)

        for ind in evaluation.index.levels[0]:
            title = f"Series {ind}"
            df = evaluation.loc[ind].copy()
            df.sort_values(sort_by, ascending=reverse, inplace=True)
            df["position"] = np.arange(1, len(df) + 1)
            df.reset_index(inplace=True)
            df.set_index("position", inplace=True)
            print_pandas_dataframe(df, title)
            console.print()

        print_pandas_dataframe(evaluation_total, "Total")
    except KeyError:
        console.print_exception()


@evaluate.command()
@pass_backend
@click.option(
    "-f",
    "--output-file",
    help="File to write the generated report to.",
    default="report.html",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
)
def report(backend: Backend, output_file: Path):
    """Create a HTML report page which displays the evaluated game results."""
    code = plugins.report_standalone(backend)
    output_file.write_text(code)
