from pathlib import Path

from .app import app, get_nav_items
from flask import render_template


@app.route("/")
def index():
    return render_template(
        "index.html",
        nav_items=get_nav_items(),
    )
