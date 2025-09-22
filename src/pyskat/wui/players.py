from fastapi import Form
from fastapi.requests import Request
from fastapi.routing import APIRouter
from typing import Annotated
from starlette.responses import RedirectResponse
from pyskat.wui.jinja import RenderTemplateDep
from sqlmodel import select

from pyskat.dependencies import DbSessionDep
from pyskat.data_model import (
    Player,
    PlayerPublic,
    PlayerCreate,
    PlayerUpdate,
    PlayerPublicDeep,
)

router = APIRouter(prefix="/players", tags=["player"])


@router.get("/")
def wui_players(render_template: RenderTemplateDep, db: DbSessionDep):
    players = db.exec(select(Player)).all()
    return render_template("players.html", players=players)
