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
    default=Path("pyskat_db.json"),
)
def main(ctx, database_file: Path):
    ctx.obj = Backend(database_file)


@main.command()
@click.option("-p", "--player-count", type=click.INT, default=13)
@click.option("-s", "--series-count", type=click.INT, default=5)
@pass_backend
def fake_data(backend, player_count: int, series_count: int):
    backend.fake_data(player_count, series_count)