from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from pyskat.data_model.unset import Unset, UNSET
from pyskat.data_model.links import TablePlayerLink

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.series import Series
    from pyskat.data_model.result import Result

__all__ = ["Table", "TablePublic", "TableCreate", "TableUpdate"]


class TableBase(SQLModel):
    series_id: int | None = Field(gt=0, default=None, foreign_key="series.id")
    remarks: str = Field(default="")


class Table(TableBase, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)

    players: list["Player"] = Relationship(link_model=TablePlayerLink, back_populates="tables")
    results: list["Result"] = Relationship(back_populates="table")
    series: "Series" = Relationship(back_populates="tables")

    @property
    def player_ids(self) -> list[int]:
        return [p.id for p in self.players if p.id is not None]

    @property
    def size(self) -> int:
        return len(self.player_ids)


class TablePublic(TableBase):
    id: int = Field(gt=0, primary_key=True)
    size: int


class TableCreate(TableBase):
    pass


class TableUpdate(TableBase):
    series_id: int | Unset = Field(gt=0, default=UNSET)
    remarks: str | Unset = UNSET
