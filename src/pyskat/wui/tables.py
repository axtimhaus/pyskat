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
