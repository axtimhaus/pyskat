from fastapi import FastAPI

from pyskat.api.dependencies import Dependencies
from pyskat.settings import Settings
from pyskat.api import player
from pyskat.api import match
from pyskat.api import session
from pyskat.api import result


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()

    dependencies = Dependencies(settings)
    app.include_router(player.create_router(dependencies))
    app.include_router(match.create_router(dependencies))
    app.include_router(session.create_router(dependencies))
    app.include_router(result.create_router(dependencies))

    return app
