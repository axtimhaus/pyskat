from pydantic import ValidationError

from .app import get_nav_items
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

bp = Blueprint("players", __name__, url_prefix="/players")


@bp.route("/", methods=["GET", "POST"])
def index():
    players_list = g.backend.players.all()

    return render_template(
        "players.html",
        nav_items=get_nav_items(active="players"),
        players=players_list,
    )


@bp.post("/add")
def add():
    try:
        g.backend.players.add(
            name=request.form["name"],
            active=request.form["active"],
            remarks=request.form["remarks"],
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
        g.backend.players.update(
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
        g.backend.players.remove(id)
    except KeyError:
        flash_player_not_found(id)
    return redirect_to_index()


def flash_player_not_found(id: int):
    flash(f"Player {id} not found.", "danger")


def redirect_to_index():
    return redirect(url_for("players.index"))


def flash_validation_error(error: ValidationError):
    validation_messages = [format_validation_message(e) for e in error.errors()]
    flash("Submitted data was invalid:\n\n" + "\n".join(validation_messages))


def format_validation_message(e: dict):
    loc = ", ".join(e["loc"])
    return f"{loc}: {e['msg']}"
