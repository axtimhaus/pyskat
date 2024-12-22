import typer
from typer import Typer

from pyskat.settings import Settings

api = Typer()


@api.command()
def serve(ctx: typer.Context):
    from pyskat.api.app import create_app
    from uvicorn import run

    app = create_app(ctx.find_object(Settings))
    run(app)
