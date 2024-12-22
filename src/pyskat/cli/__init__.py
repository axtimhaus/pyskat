import typer

from pyskat.cli.api import api
from pyskat.settings import Settings

main = typer.Typer()
main.add_typer(api, name="api")


@main.callback()
def main_callback(
    ctx: typer.Context,
    database_url: str = "sqlite:///:memory:",
) -> None:
    ctx.obj = Settings(database_url=database_url)
