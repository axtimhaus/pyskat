from dataclasses import dataclass

from flask import flash
from pydantic import ValidationError


@dataclass
class NavItem:
    id: str
    caption: str
    link: str
    active: bool = False


def flash_validation_error(error: ValidationError):
    validation_messages = [format_validation_message(e) for e in error.errors()]
    flash("Submitted data was invalid.", "danger")
    for message in validation_messages:
        flash(message, "danger")


def format_validation_message(e: dict):
    loc = ", ".join(e["loc"])
    return f"{loc}: {e['msg']}"
