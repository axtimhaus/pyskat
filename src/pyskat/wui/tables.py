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

bp = Blueprint("tables", __name__, url_prefix="/tables")


@bp.get("/", defaults=dict(session_id=None))
@bp.get("/<int:session_id>")
def index(session_id):
    session_id = session_id or session.get("current_session", None)

    if session_id:
        session = g.backend.session(g.session).get(session_id)
        tables_list = g.backend.tables(g.session).all_for_session(session_id)
        results = g.backend.results(g.session).all_for_session(session_id)
    else:
        flash(
            "Please select a session on the session page to use this page.", "warning"
        )
        tables_list = []
        results = []
        session = None

    players = g.backend.players(g.session).all()

    return render_template(
        "tables.html",
        session=session,
        tables=tables_list,
        players={p.id: p for p in players},
        results={r.player_id: r for r in results},
    )


@bp.post("/add", defaults=dict(session_id=None))
@bp.post("/add/<int:session_id>")
def add(session_id):
    session_id = session_id or session.get("current_session", None)

    try:
        player1_id = request.form["player1_id"]
        player2_id = request.form["player2_id"]
        player3_id = request.form["player3_id"]
        player4_id = request.form["player4_id"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables(g.session).add(
            session_id=session_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=(player4_id != "" and player4_id != "0") or None,
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(session_id)


@bp.post("/update/<int:session_id>/<int:table_id>")
def update(session_id: int, table_id: int):
    session_id = session_id or session.get("current_session", None)

    try:
        player1_id = request.form["player1_id"]
        player2_id = request.form["player2_id"]
        player3_id = request.form["player3_id"]
        player4_id = request.form["player4_id"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables(g.session).update(
            session_id=session_id,
            id=table_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=(player4_id != "" and player4_id != "0") or None,
            remarks=remarks,
        )
    except KeyError:
        flash_table_not_found(session_id, table_id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(session_id)


@bp.post("/remove/<int:session_id>/<int:table_id>")
def remove(session_id: int, table_id: int):
    try:
        g.backend.tables(g.session).remove(session_id, table_id)
    except KeyError:
        flash_table_not_found(session_id, table_id)
    return redirect_to_index(session_id)


def flash_table_not_found(session_id: int, table_id: int):
    flash(f"Match {session_id}/{table_id} not found.", "danger")


def redirect_to_index(session_id):
    if session_id == session.get("current_session"):
        session_id = None
    return redirect(url_for("tables.index", session_id=session_id))


@bp.get("/check", defaults=dict(session_id=None))
@bp.get("/check/<int:session_id>")
def check(session_id):
    session_id = session_id or session.get("current_session", None)
    tables = g.backend.tables(g.session).all_for_session(session_id)

    is_valid = True
    session_players = []

    for t in tables:
        table_players = []

        for p in t.player_ids:
            if p in table_players:
                flash_player_multiply_present_in_table(t.table_id, p)
                is_valid = False
            else:
                table_players.append(p)
            if p in session_players:
                flash_player_multiply_present_in_session(t.table_id, p)
                is_valid = False
            else:
                session_players.append(p)

    if is_valid:
        flash("Current table distribution is valid.", "success")
    return redirect_to_index(session_id)


def flash_player_multiply_present_in_table(table_id: int, player_id: int):
    player = g.backend.players(g.session).get(player_id)
    flash(
        f"Player {player.name} ({player.id}) is defined multiple times at table {table_id}.",
        "warning",
    )


def flash_player_multiply_present_in_session(table_id: int, player_id: int):
    player = g.backend.players(g.session).get(player_id)
    flash(
        f"Player {player.name} ({player.id}) is defined multiple times in session (duplicate at table {table_id}).",
        "warning",
    )


@bp.post("/shuffle", defaults=dict(session_id=None))
@bp.post("/shuffle/<int:session_id>")
def shuffle(session_id):
    session_id = session_id or session.get("current_session", None)

    try:
        include = [int(e) for e in request.form.getlist("include")]
        exclude = [int(e) for e in request.form.getlist("exclude")]
        include_only = [int(e) for e in request.form.getlist("include_only")]
        active_only = request.form.get("active_only", False, bool)
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables(g.session).shuffle_players_for_session(
            session_id=session_id,
            active_only=active_only,
            include=include,
            exclude=exclude,
            include_only=include_only,
        )
    except ValueError as e:
        flash(str(e), "danger")

    return redirect_to_index(session_id)
