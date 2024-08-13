from datetime import datetime

from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, flash, redirect, url_for, session

bp = Blueprint("series", __name__, url_prefix="/series")


@bp.route("/", methods=["GET", "POST"])
def index():
    series_list = g.backend.series.all()

    return render_template(
        "series.html",
        series=series_list,
        now=datetime.today().isoformat(sep=" ", timespec="minutes")
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
        g.backend.series.add(
            name=name,
            date=date,
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
        g.backend.series.update(
            id=id,
            name=name,
            date=date,
            remarks=remarks,
        )
    except KeyError:
        flash_series_not_found(id)
    except ValidationError as e:
        flash_validation_error(e)

    return redirect_to_index()


@bp.post("/remove/<int:id>")
def remove(id: int):
    try:
        g.backend.series.remove(id)
    except KeyError:
        flash_series_not_found(id)
    return redirect_to_index()

@bp.get("/get/<int:id>")
def set(id):
    session["current_series"] = id


def flash_series_not_found(id: int):
    flash(f"Series {id} not found.", "danger")


def redirect_to_index():
    return redirect(url_for("series.index"))
