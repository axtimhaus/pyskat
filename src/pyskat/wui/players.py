from .app import get_nav_items
from flask import render_template, g, request, Blueprint

bp = Blueprint("players", __name__, url_prefix="/players")


@bp.route("/", methods=["GET", "POST"])
def players():
    edit_id = request.args.get("edit", None)

    if request.method == "POST":
        if edit_id:
            g.backend.players.update(
                id=int(edit_id),
                name=request.form["name"],
                remarks=request.form["remarks"],
            )
        else:
            g.backend.players.update(
                name=request.form["name"],
                remarks=request.form["remarks"],
            )

    if edit_id:
        try:
            edit_player = g.backend.players.get(edit_id)
        except KeyError:
            edit_player = None
    else:
        edit_player = None

    remove_id = request.args.get("remove", None)
    if remove_id:
        try:
            g.backend.players.remove(int(remove_id))
        except KeyError:
            pass

    players_list = g.backend.players.all()

    return render_template(
        "players.html",
        nav_items=get_nav_items(active="players"),
        players=players_list,
        edit_player=edit_player,
    )
