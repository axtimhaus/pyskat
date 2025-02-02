from sqlalchemy.orm import foreign
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

from pyskat.data_model.unset import Unset, UNSET

if TYPE_CHECKING:
    from pyskat.data_model.player import Player
    from pyskat.data_model.series import Series
    from pyskat.data_model.result import Result

__all__ = ["Table", "TablePublic", "TableCreate", "TableUpdate"]


class TableBase(SQLModel):
    series_id: int | None = Field(gt=0, default=None, foreign_key="series.id")
    player1_id: int = Field(gt=0, foreign_key="player.id")
    player2_id: int = Field(gt=0, foreign_key="player.id")
    player3_id: int = Field(gt=0, foreign_key="player.id")
    player4_id: int | None = Field(gt=0, default=None, foreign_key="player.id")
    remarks: str = Field(default="")


class Table(TableBase, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)

    results: list["Result"] = Relationship(back_populates="table")
    series: Optional["Series"] = Relationship(back_populates="tables")

    player1: "Player" = Relationship(sa_relationship_kwargs={"foreign_keys": "Table.player1_id"})
    player2: "Player" = Relationship(sa_relationship_kwargs={"foreign_keys": "Table.player2_id"})
    player3: "Player" = Relationship(sa_relationship_kwargs={"foreign_keys": "Table.player3_id"})
    player4: Optional["Player"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Table.player4_id"})

    @property
    def player_ids(self) -> list[int]:
        if self.player4_id is not None:
            return [self.player1_id, self.player2_id, self.player3_id, self.player4_id]
        return [self.player1_id, self.player2_id, self.player3_id]

    @property
    def players(self) -> list[int]:
        if self.player4 is not None:
            return [self.player1, self.player2, self.player3, self.player4]
        return [self.player1, self.player2, self.player3]

    @property
    def size(self) -> int:
        return len(self.player_ids)


class TablePublic(TableBase):
    id: int = Field(gt=0, primary_key=True)
    size: int


class TableCreate(TableBase):
    pass


class TableUpdate(TableBase):
    series_id: int | None | Unset = Field(gt=0, default=UNSET)
    player1_id: int | Unset = Field(gt=0, default=UNSET)
    player2_id: int | Unset = Field(gt=0, default=UNSET)
    player3_id: int | Unset = Field(gt=0, default=UNSET)
    player4_id: int | None | Unset = Field(gt=0, default=UNSET)
    remarks: str | Unset = UNSET
