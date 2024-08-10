from datetime import datetime
from pathlib import Path

import click
import numpy as np
from click import pass_context
from click.shell_completion import CompletionItem

from ..backend import Backend, evaluate_results
from ..backend.data_model import to_pandas, Series, Table, Player
from ..rich import console, print_pandas_dataframe
from .config import APP_DIR
from .main import pass_backend

SERIES_NAME_HELP = "A name for the series."
SERIES_DATE_HELP = "The date or time stamp the series was played on."
SERIES_REMARKS_HELP = "Additional remarks."


def complete_series_id(ctx: click.Context, param, incomplete):
    backend: Backend = ctx.find_object(Backend)
    all_series = backend.series.all()

    c = [
        CompletionItem(s.id, help=f"{s.name} on {s.date}") for s in all_series if str(s.id).startswith(str(incomplete))
    ]
    return c


series_id_argument = click.argument("series_id", type=click.INT, shell_complete=complete_series_id, required=False)


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
    type=click.DateTime(),
    prompt=True,
    default=datetime.today(),
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
    date: datetime,
    remarks: str,
    all_players: bool,
):
    """Create a new series and set it as current."""
    id = backend.series.add(name, date, remarks)
    current_series.set(id)

    if all_players:
        backend.series.all_players(id)


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
    series_id: int | None,
    player_ids: list[int],
    all: bool,
):
    """Add players to a series."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    if all:
        backend.series.all_players(series_id)
        return

    elif not player_ids:
        player_ids = [int(s) for s in click.prompt("Player IDs").split()]

    try:
        backend.series.add_players(series_id, player_ids)
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
    series_id: int | None,
    player_ids: list[int],
    all: bool,
):
    """Remove players from a series."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    if all:
        backend.series.clear_players()
        return

    elif not player_ids:
        player_ids = [int(s) for s in click.prompt("Player IDs").split()]

    try:
        backend.series.remove_players(series_id, player_ids)
    except KeyError:
        console.print_exception()


@series.command()
@pass_backend
def list(backend: Backend):
    """List all series in database."""
    all_series = backend.series.all()
    df = to_pandas(all_series, Series, "id")
    print_pandas_dataframe(df)


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
@pass_context
def shuffle_players(ctx: click.Context, backend: Backend, current_series: CurrentSeries, series_id: int | None):
    """Generate a random player distribution of players to tables."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    old = backend.tables.all_for_series(series_id)
    if old:
        if not click.confirm(
            "There is already a player-to-table distribution for this series. Proceeding will overwrite that."
        ):
            return

    backend.tables.shuffle_players_for_series(series_id)
    print_series_table(backend, series_id)


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
def list_tables(backend: Backend, current_series: CurrentSeries, series_id: int | None):
    """Generate a random player distribution of players to tables."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)
    print_series_table(backend, series_id)


def print_series_table(backend: Backend, id: int):
    df = to_pandas(backend.tables.all_for_series(id), Table, ["table_id"])
    df.drop("series_id", axis=1, inplace=True)

    all_players = to_pandas(backend.players.all(), Player, "id")

    def get_player_name(pid):
        if pid == 0:
            return ""
        try:
            return f"{all_players.loc[i]['name']} ({i})"
        except KeyError:
            return "<unknown player>"

    for i in range(1, 5):
        df[f"player{i}"] = df[f"player{i}_id"].map(get_player_name)
        df.drop(f"player{i}_id", inplace=True, axis=1)

    df.sort_index(axis=1, inplace=True)
    print_pandas_dataframe(df)


@series.command()
@series_id_argument
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
@pass_current_series
@pass_backend
def evaluate(backend: Backend, current_series: CurrentSeries, series_id: int, sort_by: str | None, reverse: bool):
    """Evaluate and display all game results."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    try:
        df = evaluate_results(backend)
        df.reset_index(inplace=True)
        df = df[df.series_id == series_id]
        df.drop("series_id", axis=1, inplace=True)
        df.sort_values(sort_by, ascending=reverse, inplace=True)
        df["position"] = np.arange(1, len(df) + 1)
        df.set_index("position", inplace=True)
        print_pandas_dataframe(df, f"Series {series_id}")
    except KeyError:
        console.print_exception()
