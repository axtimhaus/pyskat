from fastapi import FastAPI

from pyskat.api.dependencies import Dependencies
from pyskat.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    dependencies = Dependencies(settings)

    from pyskat.api import players

    app.include_router(players.create_router(dependencies))

    return app
