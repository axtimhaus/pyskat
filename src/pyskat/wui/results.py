from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash, session

from ..cli.player_commands import player

bp = Blueprint("results", __name__, url_prefix="/results")


@bp.post("/add/<int:series_id>/<int:player_id>")
def add(series_id, player_id):
    try:
        points = request.form["points"]
        won = request.form["won"]
        lost = request.form["lost"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.results.add(
            series_id=series_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(series_id)


@bp.post("/update/<int:series_id>/<int:player_id>")
def update(series_id: int, player_id: int):
    series_id = series_id or session.get("current_series", None)

    try:
        points = request.form["points"]
        won = request.form["won"]
        lost = request.form["lost"]
        remarks = request.form["remarks"]
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.results.update(
            series_id=series_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
    except KeyError:
        flash_result_not_found(series_id, player_id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index(series_id)


@bp.post("/remove/<int:series_id>/<int:player_id>")
def remove(series_id: int, player_id: int):
    try:
        g.backend.results.remove(series_id, player_id)
    except KeyError:
        flash_result_not_found(series_id, player_id)
    return redirect_to_index(series_id)


def flash_result_not_found(series_id: int, player_id: int):
    flash(f"Result for player {player_id} in series {series_id} not found.", "danger")


def redirect_to_index(series_id):
    if series_id == session.get("current_series"):
        series_id = None
    return redirect(url_for("tables.index", series_id=series_id))



