from enum import Enum

__all__ = ["UNSET", "Unset"]


class Unset(Enum):
    """Type of the UNSET singleton."""

    token = 0

    def __repr__(self) -> str:
        return "UNSET"

    def __str__(self) -> str:
        return "UNSET"


UNSET = Unset.token
"""
Singleton to mark a model field as unset (avoids confusion with valid None values).
Mainly aimed for update models.
"""
