from .app import app, get_nav_items, get_backend
from flask import render_template, session, request


@app.route("/players", methods=["GET", "POST"])
def players():
    backend = get_backend()

    edit_id = request.args.get("edit", None)

    if request.method == "POST":
        if edit_id:
            backend.update_player(
                id=int(edit_id),
                name=request.form["name"],
                remarks=request.form["remarks"],
            )
        else:
            backend.add_player(
                name=request.form["name"],
                remarks=request.form["remarks"],
            )

    if edit_id:
        edit_player = backend.get_player(edit_id)
    else:
        edit_player = None

    remove_id = request.args.get("remove", None)
    if remove_id:
        backend.remove_player(int(remove_id))

    players_list = backend.list_players().itertuples()

    return render_template(
        "players.html",
        nav_items=get_nav_items(active="players"),
        players=players_list,
        edit_player=edit_player,
    )
