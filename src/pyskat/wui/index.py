from pathlib import Path

from .app import app, get_nav_items
from flask import render_template, request, session


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["database_file"] = request.form["database-file"]

    database_files = Path.cwd().glob("*.json")

    return render_template(
        "index.html",
        nav_items=get_nav_items(),
        database_files=[str(f) for f in database_files],
        current_database_file=session.get("database_file", None),
    )
