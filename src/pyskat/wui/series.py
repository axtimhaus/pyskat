from datetime import datetime

from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import (
    render_template,
    g,
    request,
    Blueprint,
    abort,
    flash,
    redirect,
    url_for,
    session,
)

bp = Blueprint("session", __name__, url_prefix="/session")


@bp.get("/")
def index():
    session_list = g.backend.session(g.session).all()

    return render_template(
        "session.html",
        session=session_list,
        now=datetime.today().isoformat(sep=" ", timespec="minutes"),
    )


@bp.post("/add")
def add():
    try:
        name = request.form["name"]
        date = request.form["date"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.session(g.session).add(
            name=name,
            date=datetime.fromisoformat(date),
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index()


@bp.post("/update/<int:id>")
def update(id: int):
    try:
        name = request.form["name"]
        date = request.form["date"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.session(g.session).update(
            id=id,
            name=name,
            date=datetime.fromisoformat(date),
            remarks=remarks,
        )
    except KeyError:
        flash_session_not_found(id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index()


@bp.post("/remove/<int:id>")
def remove(id: int):
    try:
        g.backend.session(g.session).remove(id)
    except KeyError:
        flash_session_not_found(id)
    return redirect_to_index()


@bp.post("/set-current/<int:id>")
def set_current(id):
    session["current_session"] = id
    return redirect_to_index()


def flash_session_not_found(id: int):
    flash(f"Session {id} not found.", "danger")


def redirect_to_index():
    return redirect(url_for("session.index"))
