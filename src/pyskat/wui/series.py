from .app import get_nav_items
from flask import render_template, g, request, Blueprint

bp = Blueprint("series", __name__, url_prefix="/series")


@bp.route("/", methods=["GET", "POST"])
def series():
    edit_id = request.args.get("edit", None)

    if request.method == "POST":
        if edit_id:
            series_id = int(edit_id)
            g.backend.series.update(
                id=series_id,
                name=request.form["name"],
                date=request.form["date"],
                remarks=request.form["remarks"],
            )
        else:
            series_id = g.backend.series.add(
                name=request.form["name"],
                date=request.form["date"],
                remarks=request.form["remarks"],
            )
        checked_players = [
            int(k.split("_")[1]) for k, v in request.form.items() if k.startswith("player_") and v == "on"
        ]
        g.backend.series.clear_players(series_id)
        g.backend.series.add_players(series_id, checked_players)

    if edit_id:
        edit_series = g.backend.series.get(edit_id)
    else:
        edit_series = None

    remove_id = request.args.get("remove", None)
    if remove_id:
        g.backend.series.remove(int(remove_id))

    series_list = list(g.backend.series.all())
    players_list = list(g.backend.players.all())

    return render_template(
        "series.html",
        nav_items=get_nav_items(active="series"),
        series=series_list,
        players=players_list,
        edit_series=edit_series,
    )
