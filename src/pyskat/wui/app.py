from dataclasses import dataclass

from flask import Flask

app = Flask("pyskat.wui")
app.secret_key = "abc"


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
