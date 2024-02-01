from typing import Optional

import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console


@click.group()
def result():
    pass


@result.command()
@click.option(
    "-s", "--series-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-t", "--table-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-p", "--player-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-P", "--points",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-W", "--won",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-L", "--lost",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-r", "--remarks",
    type=click.STRING,
    prompt=True,
    default="",
)
@pass_backend
def add(backend: Backend, series_id: int, table_id: int, player_id: int, points: int, won: int, lost: int,
        remarks: str):
    try:
        backend.add_result(series_id, table_id, player_id, points, won, lost, remarks)
    except KeyError:
        console.print_exception()


@result.command()
@click.option(
    "-s", "--series-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-t", "--table-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-p", "--player-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-P", "--points",
    type=click.INT,
    default=None,
)
@click.option(
    "-W", "--won",
    type=click.INT,
    default=None,
)
@click.option(
    "-L", "--lost",
    type=click.INT,
    default=None,
)
@click.option(
    "-r", "--remarks",
    type=click.STRING,
    default=None,
)
@pass_backend
def update(backend: Backend, series_id: int, table_id: int, player_id: int, points: Optional[int], won: Optional[int],
           lost: Optional[int], remarks: Optional[str]):
    try:
        if points is None:
            points = click.prompt("Points", default=backend.get_result(series_id, table_id, player_id)["points"])
        if won is None:
            won = click.prompt("Won", default=backend.get_result(series_id, table_id, player_id)["won"])
        if lost is None:
            remarks = click.prompt("Lost", default=backend.get_result(series_id, table_id, player_id)["lost"])
        if remarks is None:
            remarks = click.prompt("Remarks", default=backend.get_result(series_id, table_id, player_id)["remarks"])

        backend.update_result(series_id, table_id, player_id, points, won, lost, remarks)
    except KeyError:
        console.print_exception()


@result.command()
@click.option(
    "-s", "--series-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-t", "--table-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-p", "--player-id",
    type=click.INT,
    prompt=True,
)
@pass_backend
def remove(backend: Backend, series_id: int, table_id: int, player_id: int):
    try:
        backend.remove_result(series_id, table_id, player_id)
    except KeyError:
        console.print_exception()


@result.command()
@click.option(
    "-s", "--series-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-t", "--table-id",
    type=click.INT,
    prompt=True,
)
@click.option(
    "-p", "--player-id",
    type=click.INT,
    prompt=True,
)
@pass_backend
def get(backend: Backend, series_id: int, table_id: int, player_id: int):
    try:
        p = backend.get_result(series_id, table_id, player_id)

        console.print(p)
    except KeyError:
        console.print_exception()


@result.command()
@pass_backend
def list(backend: Backend):
    results = backend.list_results()
    console.print(results)
