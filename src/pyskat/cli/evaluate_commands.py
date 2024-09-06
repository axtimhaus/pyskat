import click
import numpy as np

from .series_commands import series_id_argument, CurrentSeries, pass_current_series
from ..backend import Backend
from ..plugins import evaluate_results
from ..rich import console, print_pandas_dataframe
from .main import pass_backend


@click.command()
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
def evaluate(backend: Backend, sort_by: str | None, reverse: bool):
    """Evaluate and display game results per series and in total."""
    try:
        evaluation = evaluate_results(backend, None)

        for ind in evaluation.index.levels[0]:
            if isinstance(ind, int):
                title = f"Series {ind}"
            elif isinstance(ind, str):
                title = ind.title()
            else:
                title = None

            df = evaluation.loc[ind].copy()
            df.sort_values(sort_by, ascending=reverse, inplace=True)
            df["position"] = np.arange(1, len(df) + 1)
            df.reset_index(inplace=True)
            df.set_index("position", inplace=True)
            print_pandas_dataframe(df, title)
            console.print()
    except KeyError:
        console.print_exception()
