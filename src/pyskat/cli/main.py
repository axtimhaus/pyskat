from pathlib import Path

import click

from ..backend import Backend

pass_backend = click.make_pass_decorator(Backend)


@click.group()
@click.pass_context
@click.option(
    "-d",
    "--database-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("pyskat.db"),
    help="The path where to store the SQLite database file.",
)
@click.option(
    "-c",
    "--connection-string",
    type=click.STRING,
    default=None,
    help="An explicit connection string to a SQL database. Takes precedence over --database-file.",
)
def main(ctx, database_file: Path, connection_string: str):
    if not connection_string:
        connection_string = f"sqlite:///{database_file.resolve()}"
    ctx.obj = Backend(connection_string)


@main.command()
@click.option("-p", "--player-count", type=click.INT, default=13)
@click.option("-s", "--series-count", type=click.INT, default=5)
@pass_backend
def fake_data(backend, player_count: int, series_count: int):
    """Adds some fake data to the current database for testing."""
    backend.fake_data(player_count, series_count)
