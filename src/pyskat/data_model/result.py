from sqlmodel import SQLModel, Field, Relationship


from typing import TYPE_CHECKING

from .unset import UNSET, Unset

if TYPE_CHECKING:
    from pyskat.data_model.table import Table
    from pyskat.data_model.player import Player


class ResultBase(SQLModel):
    points: int
    won: int = Field(ge=0)
    lost: int = Field(ge=0)
    remarks: str = ""


class Result(ResultBase, table=True):
    player_id: int = Field(default=0, gt=0, foreign_key="player.id", primary_key=True)
    table_id: int = Field(default=0, gt=0, foreign_key="table.id", primary_key=True)

    table: "Table" = Relationship(back_populates="results")
    player: "Player" = Relationship(back_populates="results")


class ResultPublic(ResultBase):
    player_id: int = Field(gt=0)
    table_id: int = Field(gt=0)


class ResultCreate(ResultBase):
    pass


class ResultUpdate(ResultBase):
    points: int | Unset = UNSET
    won: int | Unset = Field(ge=0, default=UNSET)
    lost: int | Unset = Field(ge=0, default=UNSET)
    remarks: str | Unset = UNSET
