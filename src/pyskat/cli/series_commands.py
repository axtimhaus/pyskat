from datetime import datetime
from pathlib import Path

import click
import numpy as np
from click import pass_context
from click.shell_completion import CompletionItem

from ..backend import Backend
from ..plugins import evaluate_results
from ..backend.data_model import to_pandas, Series, Table, Player
from ..rich import console, print_pandas_dataframe
from .config import APP_DIR
from .main import pass_backend
from sqlmodel import Session

SERIES_NAME_HELP = "A name for the series."
SERIES_DATE_HELP = "The date or time stamp the series was played on."
SERIES_REMARKS_HELP = "Additional remarks."


def complete_series_id(ctx: click.Context, param, incomplete):
    backend: Backend = ctx.find_object(Backend)
    with backend.get_session() as session:
        all_series = backend.series(session).all()

        c = [
            CompletionItem(s.id, help=f"{s.name} on {s.date}")
            for s in all_series
            if str(s.id).startswith(str(incomplete))
        ]
        return c


series_id_argument = click.argument("series_id", type=click.INT, shell_complete=complete_series_id, required=False)


class CurrentSeries:
    def __init__(self, file: Path):
        self._file = file
        file.parent.mkdir(exist_ok=True)
        try:
            self._value = int(file.read_text()) or None
        except:
            self._value = None

    def get(self) -> int | None:
        return self._value

    def set(self, id: int | None):
        self._value = id
        self._file.write_text(str(id or ""))


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
@pass_current_series
@pass_backend
def add(
    backend: Backend,
    current_series: CurrentSeries,
    name: str,
    date: datetime,
    remarks: str,
):
    """Create a new series and set it as current."""
    with backend.get_session() as session:
        id = backend.series(session).add(name, date, remarks).id
        current_series.set(id)


@series.command()
@series_id_argument
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    default=None,
    help=SERIES_NAME_HELP,
)
@click.option(
    "-d",
    "--date",
    type=click.DateTime(),
    default=None,
    help=SERIES_DATE_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    default=None,
    help=SERIES_REMARKS_HELP,
)
@pass_current_series
@pass_backend
def update(
    backend: Backend,
    current_series: CurrentSeries,
    series_id: int,
    name: str,
    date: datetime,
    remarks: str,
):
    """Create a new series and set it as current."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    with backend.get_session() as session:
        series = backend.series(session)

        try:
            if name is None:
                name = click.prompt("Name", default=series.get(series_id).name)
            if date is None:
                date = click.prompt("Date", default=series.get(series_id).date)
            if remarks is None:
                remarks = click.prompt("Remarks", default=series.get(series_id).remarks)

            series.update(series_id, name, date, remarks)
        except KeyError:
            console.print_exception()


@series.command()
@series_id_argument
@pass_backend
def remove(backend: Backend, series_id: int):
    """Remove a series from database."""
    with backend.get_session() as session:
        try:
            target = backend.series(session).get(series_id)
        except KeyError:
            console.print_exception()
            return

        if not click.confirm(
            f"Remove series {series_id} ({target.name} on {target.date})? This can not be undone. Respective tables and results will also be removed.",
            default=False,
        ):
            console.print("Aborted.")
            return

        backend.series(session).remove(series_id)
        backend.tables(session).clear_for_series(series_id)
        backend.results(session).clear_for_series(series_id)


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
def set(backend: Backend, current_series: CurrentSeries, series_id: int):
    """Set the current series to ID."""
    current_series.set(series_id)


@series.command(name="list")
@pass_backend
def _list(backend: Backend):
    """List all series in database."""
    with backend.get_session() as session:
        all_series = backend.series(session).all()
        df = to_pandas(all_series, Series, "id")
        print_pandas_dataframe(df)


@series.command()
@series_id_argument
@click.option(
    "-i",
    "--include",
    type=click.INT,
    default=[],
    multiple=True,
    help="Include an additional player explicitly. Can be given multiple times.",
)
@click.option(
    "-o",
    "--include-only",
    type=click.INT,
    default=None,
    multiple=True,
    help="Include an player and ignore automatically included ones. Can be given multiple times. If this is given, all other options have no effect",
)
@click.option(
    "-i",
    "--exclude",
    type=click.INT,
    default=[],
    multiple=True,
    help="Exclude an additional player explicitly. Can be given multiple times.",
)
@click.option(
    "--active-only/--inactive-also",
    type=click.BOOL,
    default=True,
    help="Include only active or also inactive players.",
)
@pass_current_series
@pass_backend
@pass_context
def shuffle_tables(
    ctx: click.Context,
    backend: Backend,
    current_series: CurrentSeries,
    series_id: int | None,
    include: tuple[int],
    exclude: tuple[int],
    include_only: tuple[int],
    active_only: bool,
):
    """Generate a random player distribution of players to tables."""
    with backend.get_session() as session:
        if not series_id:
            series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

        old = backend.tables(session).all_for_series(series_id)
        if old:
            if not click.confirm(
                "There is already a player-to-table distribution for this series. Proceeding will overwrite that."
            ):
                return

        backend.tables(session).shuffle_players_for_series(
            series_id,
            active_only=active_only,
            include=include or None,
            exclude=exclude or None,
            include_only=include_only or None,
        )
        print_series_table(backend, series_id)


@series.command()
@series_id_argument
@pass_current_series
@pass_backend
def list_tables(backend: Backend, current_series: CurrentSeries, series_id: int | None):
    """Generate a random player distribution of players to tables."""
    with backend.get_session() as session:
        if not series_id:
            series_id = click.prompt("Id", default=current_series.get(), type=click.INT)
        print_series_table(backend, session, series_id)


def print_series_table(backend: Backend, session: Session, id: int):
    df = to_pandas(backend.tables(session).all_for_series(id), Table, ["table_id"])
    df.drop("series_id", axis=1, inplace=True)

    all_players = to_pandas(backend.players(session).all(), Player, "id")

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
def evaluate(
    backend: Backend,
    current_series: CurrentSeries,
    series_id: int,
    sort_by: str | None,
    reverse: bool,
):
    """Evaluate and display all game results."""
    if not series_id:
        series_id = click.prompt("Id", default=current_series.get(), type=click.INT)

    try:
        df = evaluate_results(backend, series_id)
        df.reset_index(inplace=True)
        df.drop("series_id", axis=1, inplace=True)
        df.sort_values(sort_by, ascending=reverse, inplace=True)
        df["position"] = np.arange(1, len(df) + 1)
        df.set_index("position", inplace=True)
        print_pandas_dataframe(df, f"Series {series_id}")
    except KeyError:
        console.print_exception()
