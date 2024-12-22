from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from .unset import Unset, UNSET

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.table import Table
    from pyskat.data_model.result import Result

__all__ = ["Series", "SeriesPublic", "SeriesCreate", "SeriesUpdate"]


class SeriesBase(SQLModel):
    name: str = ""
    date: datetime
    remarks: str = ""


class Series(SeriesBase, table=True):
    id: int | None = Field(ge=0, default=None, primary_key=True)

    tables: list["Table"] = Relationship(back_populates="series")

    @property
    def players(self) -> list["Player"]:
        return [p for t in self.tables for p in t.players]


class SeriesPublic(SeriesBase):
    id: int = Field(ge=0, primary_key=True)


class SeriesCreate(SeriesBase):
    pass


class SeriesUpdate(SeriesBase):
    name: str | Unset = UNSET
    date: datetime | Unset = UNSET
    remarks: str | Unset = UNSET
