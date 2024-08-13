from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

bp = Blueprint("tables", __name__, url_prefix="/tables")


@bp.route("/", methods=["GET", "POST"])
def index():
    tables_list = g.backend.tables.all()

    return render_template(
        "tables.html",
        tables=tables_list,
    )
