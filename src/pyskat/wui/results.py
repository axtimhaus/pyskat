from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

bp = Blueprint("results", __name__, url_prefix="/results")


@bp.route("/", methods=["GET", "POST"])
def index():
    results_list = g.backend.results.all()

    return render_template(
        "results.html",
        results=results_list,
    )
