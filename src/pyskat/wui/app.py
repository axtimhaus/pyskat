import tomllib
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, session, render_template, url_for

from pyskat.backend import Backend
from . import default_config


def create_app(
    backend: Backend,
    instance_directory: Path,
):
    app = Flask("pyskat.wui", instance_relative_config=True, instance_path=str(instance_directory.resolve()))
    app.config.from_object(default_config)

    app.config.from_file("pyskat_config.toml", load=tomllib.load, silent=True)
    app.config.from_prefixed_env(prefix="PYSKAT_")

    def provide_backend():
        from flask import g

        g.backend = backend

    app.before_request(provide_backend)

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            nav_items=get_nav_items(),
        )

    from . import players

    app.register_blueprint(players.bp)

    from . import series

    app.register_blueprint(series.bp)

    return app


@dataclass
class NavItem:
    id: str
    caption: str
    link: str
    active: bool = False


def get_nav_items(active: str | None = None) -> list[NavItem]:
    items = [
        NavItem("players", "Players", "/players"),
        NavItem("series", "Series", "/series"),
        NavItem("results", "Results", "/results"),
        NavItem("evaluation", "Evaluation", "/evaluation"),
    ]

    if active:
        for i in items:
            if i.id == active:
                i.active = True
                break

    return items
