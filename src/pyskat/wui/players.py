from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

bp = Blueprint("players", __name__, url_prefix="/players")


@bp.get("/")
def index():
    players_list = g.backend.players(g.session).all()

    return render_template(
        "players.html",
        players=players_list,
    )


@bp.post("/add")
def add():
    try:
        name = request.form["name"]
        remarks = request.form["remarks"]
        active = request.form.get("active", False, bool)
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.players(g.session).add(
            name=name,
            active=active,
            remarks=remarks,
        )
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index()


@bp.post("/update/<int:id>")
def update(id: int):
    try:
        name = request.form["name"]
        remarks = request.form["remarks"]
        active = request.form.get("active", False, bool)
    except KeyError:
        abort(400, description="Invalid form data submitted.")

    try:
        g.backend.players(g.session).update(
            id=id,
            name=name,
            active=active,
            remarks=remarks,
        )
    except KeyError:
        flash_player_not_found(id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index()


@bp.post("/remove/<int:id>")
def remove(id: int):
    try:
        g.backend.players(g.session).remove(id)
    except KeyError:
        flash_player_not_found(id)
    return redirect_to_index()


def flash_player_not_found(id: int):
    flash(f"Player {id} not found.", "danger")


def redirect_to_index():
    return redirect(url_for("players.index"))
