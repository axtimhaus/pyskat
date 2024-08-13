from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

bp = Blueprint("evaluation", __name__, url_prefix="/evaluation")


@bp.route("/", methods=["GET", "POST"])
def index():
    evaluation_list = g.backend.evaluation.all()

    return render_template(
        "evaluation.html",
        evaluation=evaluation_list,
    )
