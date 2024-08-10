import click
import pandas as pd
from click.shell_completion import CompletionItem

from ..backend import Backend
from ..backend.data_model import to_pandas, Player
from ..rich import console, print_pandas_dataframe
from .main import pass_backend

PLAYER_NAME_HELP = "Name (full name, nickname, ...)."
PLAYER_REMARKS_HELP = "Additional remarks if needed."


def complete_player_id(ctx: click.Context, param, incomplete):
    backend: Backend = ctx.find_object(Backend)
    players = backend.players.all()

    c = [CompletionItem(p.id, help=p.name) for p in players if str(p.id).startswith(str(incomplete))]
    return c


player_id_argument = click.argument("player_id", type=click.INT, shell_complete=complete_player_id)


@click.group()
def player():
    """Manage players."""


@player.command()
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    prompt=True,
    help=PLAYER_NAME_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    prompt=True,
    default="",
    help=PLAYER_REMARKS_HELP,
)
@pass_backend
def add(backend: Backend, name: str, remarks: str):
    """Add a new player to database."""
    try:
        backend.players.add(name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@player_id_argument
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    default=None,
    help=PLAYER_NAME_HELP,
)
@click.option(
    "-r",
    "--remarks",
    type=click.STRING,
    default=None,
    help=PLAYER_REMARKS_HELP,
)
@pass_backend
def update(backend: Backend, player_id: int, name: str | None, remarks: str | None):
    """Update an existing player in database."""
    try:
        if name is None:
            name = click.prompt("Name", default=backend.players.get(player_id).name)
        if remarks is None:
            remarks = click.prompt("Remarks", default=backend.players.get(player_id).remarks)

        backend.players.update(player_id, name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@player_id_argument
@pass_backend
def remove(backend: Backend, player_id: int):
    """Remove a player from database."""
    try:
        backend.players.remove(player_id)
    except KeyError:
        console.print_exception()


@player.command()
@player_id_argument
@pass_backend
def get(backend: Backend, player_id: int):
    """Get a player from database."""
    try:
        p = backend.players.get(player_id)

        console.print(p)
    except KeyError:
        console.print_exception()


@player.command()
@pass_backend
def list(backend: Backend):
    """List all players in database."""
    players = backend.players.all()
    df = to_pandas(players, Player, "id")
    print_pandas_dataframe(df)
