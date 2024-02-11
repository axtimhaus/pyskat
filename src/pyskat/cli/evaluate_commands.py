from typing import Optional

import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe


@click.group()
def evaluate():
    """Evaluate game results."""
    pass


@evaluate.command()
@click.option(
    "-s",
    "--sort-by",
    type=click.STRING,
    default=None,
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
def results(backend: Backend, sort_by: Optional[str], reverse: bool):
    """Evaluate and display all game results."""
    try:
        evaluation = backend.evaluate_results()

        print_pandas_dataframe(evaluation.sort_values(sort_by, ascending=reverse))
    except KeyError:
        console.print_exception()


@evaluate.command()
@click.option(
    "-s",
    "--sort-by",
    type=click.STRING,
    default=None,
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
def total(backend: Backend, sort_by: Optional[str], reverse: bool):
    """Evaluate and display game results per series and in total."""
    try:
        evaluation = backend.evaluate_total()

        for ind in evaluation.columns.levels[0]:
            if isinstance(ind, int):
                title = f"Series {ind}"
            elif isinstance(ind, str):
                title = ind.title()
            else:
                title = None

            print_pandas_dataframe(
                evaluation[ind].sort_values(sort_by, ascending=reverse), title
            )
            console.print()
    except KeyError:
        console.print_exception()
