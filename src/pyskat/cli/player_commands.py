from typing import Optional

import click
from click.shell_completion import CompletionItem

from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe

PLAYER_NAME_HELP = "Name (full name, nickname, ...)."
PLAYER_REMARKS_HELP = "Additional remarks if needed."


def complete_player_id(ctx: click.Context, param, incomplete):
    backend: Backend = ctx.find_object(Backend)
    players = backend.list_players()
    players.reset_index(inplace=True)
    players["matches"] = players["id"].apply(
        lambda i: str(i).startswith(str(incomplete))
    )
    players.query("matches", inplace=True)

    c = [CompletionItem(t[0], help=t[1]) for t in players.itertuples(index=False)]
    return c


player_id_argument = click.argument(
    "player_id", type=click.INT, shell_complete=complete_player_id
)


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
def update(
    backend: Backend, player_id: int, name: Optional[str], remarks: Optional[str]
):
    """Update an existing player in database."""
    try:
        if name is None:
            name = click.prompt("Name", default=backend.get_player(player_id)["name"])
        if remarks is None:
            remarks = click.prompt(
                "Remarks", default=backend.get_player(player_id)["remarks"]
            )

        backend.update_player(player_id, name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@player_id_argument
@pass_backend
def remove(backend: Backend, player_id: int):
    """Remove a player from database."""
    try:
        backend.remove_player(player_id)
    except KeyError:
        console.print_exception()


@player.command()
@player_id_argument
@pass_backend
def get(backend: Backend, player_id: int):
    """Get a player from database."""
    try:
        p = backend.get_player(player_id)

        console.print(p)
    except KeyError:
        console.print_exception()


@player.command()
@pass_backend
def list(backend: Backend):
    """List all players in database."""
    players = backend.list_players()
    print_pandas_dataframe(players)
