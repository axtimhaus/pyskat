from typing import Optional

import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe

PLAYER_ID_HELP = "Unique player ID."
PLAYER_NAME_HELP = "Name (full name, nickname, ...)."
PLAYER_REMARKS_HELP = "Additional remarks if needed."


@click.group()
def player():
    """Manage players."""
    pass


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
        backend.add_player(name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@click.option(
    "-i",
    "--id",
    type=click.INT,
    prompt=True,
    help=PLAYER_ID_HELP,
)
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
def update(backend: Backend, id: int, name: Optional[str], remarks: Optional[str]):
    """Update an existing player in database."""
    try:
        if name is None:
            name = click.prompt("Name", default=backend.get_player(id)["name"])
        if remarks is None:
            remarks = click.prompt("Remarks", default=backend.get_player(id)["remarks"])

        backend.update_player(id, name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@click.option(
    "-i",
    "--id",
    type=click.INT,
    prompt=True,
    help=PLAYER_ID_HELP,
)
@pass_backend
def remove(backend: Backend, id: int):
    """Remove a player from database."""
    try:
        backend.remove_player(id)
    except KeyError:
        console.print_exception()


@player.command()
@click.option(
    "-i",
    "--id",
    type=click.INT,
    prompt=True,
    help=PLAYER_ID_HELP,
)
@pass_backend
def get(backend: Backend, id: int):
    """Get a player from database."""
    try:
        p = backend.get_player(id)

        console.print(p)
    except KeyError:
        console.print_exception()


@player.command()
@pass_backend
def list(backend: Backend):
    """List all players in database."""
    players = backend.list_players()
    print_pandas_dataframe(players)
