from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash, session

bp = Blueprint("tables", __name__, url_prefix="/tables")


@bp.get("/", defaults=dict(series_id=None))
@bp.get("/<int:series_id>")
def index(series_id):
    series_id = series_id or session.get("current_series", None)

    if series_id:
        tables_list = g.backend.tables.all_for_series(series_id)
    else:
        flash("Please select a series on the series page to use this page.", "warning")
        tables_list = []

    players=g.backend.players.all()
    results=g.backend.results.all_for_series(series_id)

    return render_template(
        "tables.html",
        tables=tables_list,
        players={p.id: p for p in players},
        results={r.table_id : r for r in results}
    )
