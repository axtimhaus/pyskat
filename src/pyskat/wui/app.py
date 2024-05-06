import json
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, session

from pyskat.backend import Backend
from . import default_config

app = Flask("pyskat.wui")
app.config.from_object(default_config)

CWD = Path.cwd()

if (CWD / "pyskat_config.json").exists():
    app.config.from_file(CWD / "pyskat_config.json", load=json.load)


app.config.from_prefixed_env(prefix="PYSKAT_")


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


_backends = dict()


def get_backend():
    db_file = app.config["DATABASE_FILE"]
    b = _backends.get(db_file, None)

    if not b:
        b = Backend(db_file)
        _backends[db_file] = b

    return b
