from .app import app, get_nav_items
from flask import render_template


@app.route("/players")
def players():
    return render_template("players.html", nav_items=get_nav_items(active="players"))
