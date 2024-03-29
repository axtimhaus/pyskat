from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from click.shell_completion import CompletionItem

from .config import APP_DIR
from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe

SERIES_NAME_HELP = "A name for the series."
SERIES_DATE_HELP = "The date or time stamp the series was played on."
SERIES_REMARKS_HELP = "Additional remarks."


def complete_series_id(ctx: click.Context, param, incomplete):

    backend: Backend = ctx.find_object(Backend)
    df = backend.list_series()
    df.reset_index(inplace=True)
    df["matches"] = df["id"].apply(lambda i: str(i).startswith(str(incomplete)))
    df.query("matches", inplace=True)

    c = [CompletionItem(t[0], help=t[1]) for t in df.itertuples(index=False)]
    return c


series_id_argument = click.argument(
    "series_id", type=click.INT, shell_complete=complete_series_id, required=False
)


class CurrentSeries:
    def __init__(self, file: Path):
        self._file = file
        file.parent.mkdir(exist_ok=True)
        try:
            self._value = int(file.read_text())
        except:
            self._value = None

    def get(self) -> int:
        return self._value

    def set(self, id: int):
        self._value = id
        self._file.write_text(str(id))


pass_current_series = click.make_pass_decorator(CurrentSeries)


@click.group()
@click.option(
    "--current-series-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=APP_DIR / Path("current_series"),
)
@click.pass_context
def series(ctx: click.Context, current_series_file: Path):
    """Generate and manage game series."""

    ctx.obj = CurrentSeries(current_series_file)


@series.command()
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    prompt=True,
    default="",
    help=SERIES_NAME_HELP,
)
@click.option(
    "-d",
    "--date",
    type=click.STRING,
    prompt=True,
    default=datetime.today().strftime("%Y-%m-%d"),
    help=SERIES_DATE_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    prompt=True,
    default="",
    help=SERIES_REMARKS_HELP,
)
@click.option(
    "-a",
    "--all-players",
    type=click.BOOL,
    is_flag=True,
    prompt=True,
    default=False,
    help="Whether to add all players to new series.",
)
@pass_current_series
@pass_backend
def add(
    backend: Backend,
    current_series: CurrentSeries,
    name: str,
    date: str,
    remarks: str,
    all_players: bool,
):
    """Create a new series and set it as current."""
    id = backend.add_series(name, date, remarks)
    current_series.set(id)

    if all_players:
        backend.add_players_to_series(id, "all")


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
def set(backend: Backend, current_series: CurrentSeries, series_id: int):
    """Set the current series to ID."""
    current_series.set(series_id)


@series.command()
@series_id_argument
@click.option(
    "-a",
    "--all",
    type=click.BOOL,
    default=False,
    is_flag=True,
)
@click.argument(
    "player-ids",
    type=click.INT,
    nargs=-1,
)
@pass_current_series
@pass_backend
def add_players(
    backend: Backend,
    current_series: CurrentSeries,
    series_id: Optional[int],
    player_ids: list[int],
    all: bool,
):
    """Add players to a series."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    if all:
        player_ids = "all"

    elif not player_ids:
        player_ids = [int(s) for s in click.prompt("Player IDs").split()]

    try:
        backend.add_players_to_series(series_id, player_ids)
    except KeyError:
        console.print_exception()


@series.command()
@series_id_argument
@click.option(
    "-a",
    "--all",
    type=click.BOOL,
    default=False,
    is_flag=True,
)
@click.argument(
    "player-ids",
    type=click.INT,
    nargs=-1,
)
@pass_current_series
@pass_backend
def remove_players(
    backend: Backend,
    current_series: CurrentSeries,
    series_id: Optional[int],
    player_ids: list[int],
    all: bool,
):
    """Remove players from a series."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    if all:
        player_ids = "all"

    elif not player_ids:
        player_ids = [int(s) for s in click.prompt("Player IDs").split()]

    try:
        backend.remove_players_from_series(series_id, player_ids)
    except KeyError:
        console.print_exception()


@series.command()
@pass_backend
def list(backend: Backend):
    """List all series in database."""
    players = backend.list_series()
    print_pandas_dataframe(players)


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
def shuffle_players(
    backend: Backend, current_series: CurrentSeries, series_id: Optional[int]
):
    """Generate a random player distribution of players to tables."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    old = backend.list_tables(series_id)
    if not old.empty:
        if not click.confirm(
            "There is already a player-to-table distribution for this series. Proceeding will overwrite that."
        ):
            return

    backend.shuffle_players_to_tables(series_id)
    print_pandas_dataframe(backend.list_tables(series_id))
