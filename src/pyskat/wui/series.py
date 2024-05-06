from .app import app, get_nav_items, get_backend
from flask import render_template, session, request


@app.route("/series", methods=["GET", "POST"])
def series():
    backend = get_backend()

    edit_id = request.args.get("edit", None)

    if request.method == "POST":
        if edit_id:
            series_id = int(edit_id)
            backend.update_series(
                id=series_id,
                name=request.form["name"],
                date=request.form["date"],
                remarks=request.form["remarks"],
            )
        else:
            series_id = backend.add_series(
                name=request.form["name"],
                date=request.form["date"],
                remarks=request.form["remarks"],
            )
        checked_players = [
            int(k.split("_")[1])
            for k, v in request.form.items()
            if k.startswith("player_") and v == "on"
        ]
        backend.remove_players_from_series(series_id, "all")
        backend.add_players_to_series(series_id, checked_players)

    if edit_id:
        edit_series = backend.get_series(edit_id)
    else:
        edit_series = None

    remove_id = request.args.get("remove", None)
    if remove_id:
        backend.remove_series(int(remove_id))

    series_list = list(backend.list_series().itertuples())
    players_list = list(backend.list_players().itertuples())

    return render_template(
        "series.html",
        nav_items=get_nav_items(active="series"),
        series=series_list,
        players=players_list,
        edit_series=edit_series,
    )
