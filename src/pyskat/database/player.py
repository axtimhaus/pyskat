from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from .unset import Unset, UNSET

if TYPE_CHECKING:
    from .series import Series
    from .result import Result
    from .table import Table, TablePlayerLink

__all__ = ["Player", "PlayerPublic", "PlayerCreate", "PlayerUpdate"]


class PlayerBase(SQLModel):
    name: str
    active: bool = True
    remarks: str = ""


class Player(PlayerBase, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)

    results: list[Result] = Relationship(back_populates="player")
    tables: list[Table] = Relationship(link_model=TablePlayerLink, back_populates="players")

    @property
    def series(self) -> list[Series]:
        return [t.series for t in self.tables]


class PlayerPublic(PlayerBase):
    id: int = Field(gt=0)


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    name: str | Unset = UNSET
    active: bool | Unset = UNSET
    remarks: str | Unset = UNSET
