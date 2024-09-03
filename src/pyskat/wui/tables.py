from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash, session

bp = Blueprint("tables", __name__, url_prefix="/tables")


@bp.get("/", defaults=dict(series_id=None))
@bp.get("/<int:series_id>")
def index(series_id):
    series_id = series_id or session.get("current_series", None)

    if series_id:
        tables_list = g.backend.tables.all(series_id)
    else:
        flash("Please select a series on the series page to use this page.", "warning")
        tables_list = []

    players=g.backend.players.all()
    results=g.backend.results.all_for_series(series_id)
    series = g.backend.series.get(series_id)

    return render_template(
        "tables.html",
        series=series,
        tables=tables_list,
        players={p.id: p for p in players},
        results={r.player_id : r for r in results}
    )


@bp.post("/add", defaults=dict(series_id=None))
@bp.post("/add/<int:series_id>")
def add(series_id):
    series_id = series_id or session.get("current_series", None)

    try:
        player1_id = request.form["player1_id"]
        player2_id = request.form["player2_id"]
        player3_id = request.form["player3_id"]
        player4_id = request.form["player4_id"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables.add(
            series_id=series_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(series_id)


@bp.post("/update/<int:series_id>/<int:table_id>")
def update(series_id: int, table_id: int):
    series_id = series_id or session.get("current_series", None)

    try:
        player1_id = request.form["player1_id"]
        player2_id = request.form["player2_id"]
        player3_id = request.form["player3_id"]
        player4_id = request.form["player4_id"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables.update(
            series_id=series_id,
            table_id=table_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )
    except KeyError:
        flash_table_not_found(series_id, table_id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(series_id)


@bp.post("/remove/<int:series_id>/<int:table_id>")
def remove(series_id: int, table_id: int):
    try:
        g.backend.tables.remove(series_id, table_id)
    except KeyError:
        flash_table_not_found(series_id, table_id)
    return redirect_to_index(series_id)


def flash_table_not_found(series_id: int, table_id: int):
    flash(f"Table {series_id}/{table_id} not found.", "danger")


def redirect_to_index(series_id):
    if series_id == session.get("current_series"):
        series_id = None
    return redirect(url_for("tables.index", series_id=series_id))


@bp.get("/check", defaults=dict(series_id=None))
@bp.get("/check/<int:series_id>")
def check(series_id):
    series_id = series_id or session.get("current_series", None)
    tables = g.backend.tables.all(series_id)

    series_players = []

    for t in tables:
        table_players = []

        for p in t.player_ids:
            if p in table_players:
                flash_player_multiply_present_in_table(t.table_id, p)
            else:
                table_players.append(p)
            if p in series_players:
                flash_player_multiply_present_in_series(t.table_id, p)
            else:
                series_players.append(p)

    return redirect_to_index(series_id)


def flash_player_multiply_present_in_table(table_id: int, player_id: int):
    player = g.backend.players.get(player_id)
    flash(f"Player {player.name} ({player.id}) is defined multiple times at table {table_id}.", "warning")


def flash_player_multiply_present_in_series(table_id: int, player_id: int):
    player = g.backend.players.get(player_id)
    flash(f"Player {player.name} ({player.id}) is defined multiple times in series (duplicate at table {table_id}).", "warning")


@bp.post("/shuffle", defaults=dict(series_id=None))
@bp.post("/shuffle/<int:series_id>")
def shuffle(series_id):
    series_id = series_id or session.get("current_series", None)

    try:
        include = [int(e) for e in request.form.getlist("include")]
        exclude = [int(e) for e in request.form.getlist("exclude")]
        include_only = [int(e) for e in request.form.getlist("include_only")]
        active_only = request.form.get("active_only", False, bool)
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.tables.shuffle_players_for_series(
            series_id=series_id,
            active_only=active_only,
            include=include,
            exclude=exclude,
            include_only=include_only,
        )
    except ValueError as e:
        flash(str(e), "danger")

    return redirect_to_index(series_id)
