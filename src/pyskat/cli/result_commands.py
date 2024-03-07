from typing import Optional

import click

from .main import pass_backend
from .player_commands import player_id_argument
from .series_commands import series_id_argument
from ..backend import Backend
from ..rich import console, print_pandas_dataframe

RESULT_PLAYER_ID_HELP = "ID of the player."
RESULT_SERIES_ID_HELP = "ID of the series."
RESULT_POINTS_HELP = "Sum of points from game values."
RESULT_WON_HELP = "Count of won games."
RESULT_LOST_HELP = "Count of lost games."
RESULT_REMARKS_HELP = "Additional remarks if needed."


@click.group()
def result():
    """Manage game results."""
    pass


@result.command()
@player_id_argument
@series_id_argument
@click.option(
    "-p",
    "--points",
    type=click.INT,
    prompt=True,
    help=RESULT_POINTS_HELP,
)
@click.option(
    "-w",
    "--won",
    type=click.INT,
    prompt=True,
    help=RESULT_WON_HELP,
)
@click.option(
    "-l",
    "--lost",
    type=click.INT,
    prompt=True,
    help=RESULT_LOST_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    prompt=True,
    default="",
    help=RESULT_REMARKS_HELP,
)
@pass_backend
def add(
    backend: Backend,
    series_id: int,
    player_id: int,
    points: int,
    won: int,
    lost: int,
    remarks: str,
):
    """Add a new game result to database."""
    try:
        backend.add_result(series_id, player_id, points, won, lost, remarks)
    except KeyError:
        console.print_exception()


@result.command()
@player_id_argument
@series_id_argument
@click.option(
    "-p",
    "--points",
    type=click.INT,
    default=None,
    help=RESULT_POINTS_HELP,
)
@click.option(
    "-w",
    "--won",
    type=click.INT,
    default=None,
    help=RESULT_WON_HELP,
)
@click.option(
    "-l",
    "--lost",
    type=click.INT,
    default=None,
    help=RESULT_LOST_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    default=None,
    help=RESULT_REMARKS_HELP,
)
@pass_backend
def update(
    backend: Backend,
    series_id: int,
    player_id: int,
    points: Optional[int],
    won: Optional[int],
    lost: Optional[int],
    remarks: Optional[str],
):
    """Update an existing game result in database."""
    try:
        if points is None:
            points = click.prompt(
                "Points", default=backend.get_result(series_id, player_id)["points"]
            )
        if won is None:
            won = click.prompt(
                "Won", default=backend.get_result(series_id, player_id)["won"]
            )
        if lost is None:
            remarks = click.prompt(
                "Lost", default=backend.get_result(series_id, player_id)["lost"]
            )
        if remarks is None:
            remarks = click.prompt(
                "Remarks", default=backend.get_result(series_id, player_id)["remarks"]
            )

        backend.update_result(series_id, player_id, points, won, lost, remarks)
    except KeyError:
        console.print_exception()


@result.command()
@player_id_argument
@series_id_argument
@pass_backend
def remove(backend: Backend, series_id: int, player_id: int):
    """Remove a game result from database."""
    try:
        backend.remove_result(series_id, player_id)
    except KeyError:
        console.print_exception()


@result.command()
@player_id_argument
@series_id_argument
@pass_backend
def get(backend: Backend, series_id: int, player_id: int):
    """Get a game result from database."""
    try:
        p = backend.get_result(series_id, player_id)

        console.print(p)
    except KeyError:
        console.print_exception()


@result.command()
@pass_backend
def list(backend: Backend):
    """List all game results ins database."""
    results = backend.list_results()
    print_pandas_dataframe(results)
