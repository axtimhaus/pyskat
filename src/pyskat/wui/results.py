from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import (
    render_template,
    g,
    request,
    Blueprint,
    abort,
    redirect,
    url_for,
    flash,
    session,
)

bp = Blueprint("results", __name__, url_prefix="/results")


@bp.get("/", defaults=dict(session_id=None))
@bp.get("/<int:session_id>")
def index(session_id):
    session_id = session_id or session.get("current_session", None)

    if session_id:
        tables_list = g.backend.tables(g.session).all_for_session(session_id)
        results = g.backend.results(g.session).all_for_session(session_id)
    else:
        flash(
            "Please select a session on the session page to use this page.", "warning"
        )
        tables_list = []
        results = []

    players = g.backend.players(g.session).all()
    session = g.backend.session(g.session).get(session_id)

    return render_template(
        "results.html",
        session=session,
        tables=tables_list,
        players={p.id: p for p in players},
        results={r.player_id: r for r in results},
    )


@bp.post("/add/<int:session_id>/<int:player_id>")
def add(session_id, player_id):
    try:
        points = request.form["points"]
        won = request.form["won"]
        lost = request.form["lost"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.results(g.session).add(
            session_id=session_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(session_id)


@bp.post("/update/<int:session_id>/<int:player_id>")
def update(session_id: int, player_id: int):
    session_id = session_id or session.get("current_session", None)

    try:
        points = request.form["points"]
        won = request.form["won"]
        lost = request.form["lost"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.results(g.session).update(
            session_id=session_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
    except KeyError:
        flash_result_not_found(session_id, player_id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(session_id)


@bp.post("/remove/<int:session_id>/<int:player_id>")
def remove(session_id: int, player_id: int):
    try:
        g.backend.results(g.session).remove(session_id, player_id)
    except KeyError:
        flash_result_not_found(session_id, player_id)
    return redirect_to_index(session_id)


def flash_result_not_found(session_id: int, player_id: int):
    flash(f"Result for player {player_id} in session {session_id} not found.", "danger")


def redirect_to_index(session_id):
    if session_id == session.get("current_session"):
        session_id = None
    return redirect(url_for("results.index", session_id=session_id))
