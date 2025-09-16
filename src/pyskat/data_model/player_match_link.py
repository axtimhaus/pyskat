# pyright: reportIncompatibleVariableOverride=false

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.match import Match

__all__ = [
    "PlayerMatchLink",
    "PlayerMatchLinkPublic",
    "PlayerMatchLinkCreate",
    "PlayerMatchLinkUpdate",
]


class PlayerMatchLinkBase(SQLModel):
    name: str
    active: bool = True
    remarks: str = ""


class PlayerMatchLink(PlayerMatchLinkBase, table=True):
    player_id: int | None = Field(
        default=None, foreign_key="player.id", primary_key=True
    )
    match_id: int | None = Field(default=None, foreign_key="match.id", primary_key=True)


class PlayerMatchLinkPublic(PlayerMatchLinkBase):
    player_id: int
    match_id: int


class PlayerMatchLinkCreate(PlayerMatchLinkBase):
    pass
