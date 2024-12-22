from fastapi import FastAPI

from pyskat.api.dependencies import Dependencies
from pyskat.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    dependencies = Dependencies(settings)

    from pyskat.api import players
    from pyskat.api import tables
    from pyskat.api import series
    from pyskat.api import results

    app.include_router(players.create_router(dependencies))
    app.include_router(tables.create_router(dependencies))
    app.include_router(series.create_router(dependencies))
    app.include_router(results.create_router(dependencies))

    return app
