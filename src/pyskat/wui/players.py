from .app import app, get_nav_items, get_backend
from flask import render_template, session, request


@app.route("/players", methods=["GET", "POST"])
def players():
    backend = get_backend()

    edit_id = request.args.get("edit", None)

    if request.method == "POST":
        if edit_id:
            backend.players.update(
                id=int(edit_id),
                name=request.form["name"],
                remarks=request.form["remarks"],
            )
        else:
            backend.players.update(
                name=request.form["name"],
                remarks=request.form["remarks"],
            )

    if edit_id:
        try:
            edit_player = backend.players.get(edit_id)
        except KeyError:
            edit_player = None
    else:
        edit_player = None

    remove_id = request.args.get("remove", None)
    if remove_id:
        try:
            backend.players.remove(int(remove_id))
        except KeyError:
            pass

    players_list = backend.players.all()

    return render_template(
        "players.html",
        nav_items=get_nav_items(active="players"),
        players=players_list,
        edit_player=edit_player,
    )
