from typing import Optional

import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console


@click.group()
def player():
    pass


@player.command()
@click.option(
    "-i", "--id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-n", "--name",
    type=click.STRING,
    prompt=True,
)
@click.option(
    "-r", "--remarks",
    type=click.STRING,
    prompt=False,
    default=None,
)
@pass_backend
def add(backend: Backend, id: int, name: str, remarks: Optional[str]):
    try:
        backend.add_player(id, name, remarks)
    except KeyError:
        console.print_exception()


@player.command()
@click.option(
    "-i", "--id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-n", "--name",
    type=click.STRING,
    default=None,
)
@click.option(
    "-r", "--remarks",
    type=click.STRING,
    default=None,
)
@pass_backend
def update(backend: Backend, id: int, name: Optional[str], remarks: Optional[str]):
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
    "-i", "--id",
    type=click.INT,
    prompt=True,
)
@pass_backend
def remove(backend: Backend, id: int):
    try:
        backend.remove_player(id)
    except KeyError:
        console.print_exception()


@player.command()
@click.option(
    "-i", "--id",
    type=click.INT,
    prompt=True,
)
@pass_backend
def get(backend: Backend, id: int):
    try:
        p = backend.get_player(id)

        console.print(p)
    except KeyError:
        console.print_exception()


@player.command()
@pass_backend
def list(backend: Backend):
    players = backend.list_players()
    console.print(players)
