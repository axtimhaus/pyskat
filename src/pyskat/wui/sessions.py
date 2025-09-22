from datetime import datetime
from fastapi import Request
from fastapi.routing import APIRouter
from sqlmodel import select

from pyskat.wui.jinja import RenderTemplateDep
from pyskat.dependencies import DbSessionDep
from pyskat.data_model import Session, SessionPublic
from pyskat.api.session import raise_not_found


router = APIRouter(prefix="/sessions", tags=["session"])


@router.get("/")
def wui_sessions(
    render_template: RenderTemplateDep, db: DbSessionDep, request: Request
):
    sessions = db.exec(select(Session)).all()
    return render_template(
        "sessions.html",
        sessions=sessions,
        current_session_id=request.session.get("current_session_id", None),
        now=datetime.today().isoformat(sep=" ", timespec="minutes"),
    )


@router.patch("/current/{session_id}", response_model=SessionPublic)
def wui_sessions_set_current(session_id: int, db: DbSessionDep, request: Request):
    session = db.get(Session, session_id) or raise_not_found(session_id)
    request.session["current_session_id"] = session_id
    return session
