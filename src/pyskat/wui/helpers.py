from dataclasses import dataclass

from flask import flash
from pydantic import ValidationError


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


def flash_validation_error(error: ValidationError):
    validation_messages = [format_validation_message(e) for e in error.errors()]
    flash("Submitted data was invalid.", "danger")
    for message in validation_messages:
        flash(message, "danger")


def format_validation_message(e: dict):
    loc = ", ".join(e["loc"])
    return f"{loc}: {e['msg']}"
