from datetime import datetime
from typing import Iterable

import pandas as pd
from sqlmodel import SQLModel, Field, Relationship


class TablePlayerLink(SQLModel, table=True):
    table_id: int = Field(gt=0, foreign_key="table.id", primary_key=True)
    player_id: int = Field(gt=0, foreign_key="player.id", primary_key=True)


class Player(SQLModel, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)
    name: str
    active: bool = True
    remarks: str = ""

    results: list["Result"] = Relationship(back_populates="player")
    tables: list["Table"] = Relationship(
        link_model=TablePlayerLink, back_populates="players"
    )

    @property
    def series(self) -> list["Series"]:
        return [t.series for t in self.tables]


class Table(SQLModel, table=True):
    id: int | None = Field(gt=0, default=None, primary_key=True)
    series_id: int = Field(gt=0, foreign_key="series.id")
    remarks: str = Field(default="")

    players: list[Player] = Relationship(
        link_model=TablePlayerLink, back_populates="tables"
    )
    series: "Series" = Relationship(back_populates="tables")

    @property
    def player_ids(self) -> list[int]:
        return [p.id for p in self.players if p.id is not None]

    @property
    def size(self) -> int:
        return len(self.player_ids)


class Series(SQLModel, table=True):
    id: int | None = Field(ge=0, default=None, primary_key=True)
    name: str = ""
    date: datetime
    remarks: str = ""

    tables: list[Table] = Relationship(back_populates="series")
    results: list["Result"] = Relationship(back_populates="series")

    @property
    def players(self) -> list[Player]:
        return [p for t in self.tables for p in t.players]


class Result(SQLModel, table=True):
    series_id: int = Field(default=0, gt=0, foreign_key="series.id", primary_key=True)
    player_id: int = Field(default=0, gt=0, foreign_key="player.id", primary_key=True)
    points: int
    won: int = Field(ge=0)
    lost: int = Field(ge=0)
    remarks: str = ""

    series: Series = Relationship(back_populates="results")
    player: Player = Relationship(back_populates="results")


def to_pandas(
    data: SQLModel | Iterable[SQLModel],
    model_type: type[SQLModel],
    index_cols: str | list[str],
) -> pd.DataFrame:
    if isinstance(data, SQLModel):
        df = pd.DataFrame(data.model_dump())
    else:
        if not data:
            cols = list(model_type.model_fields.keys())
            index = (
                pd.Index([], name=index_cols)
                if isinstance(index_cols, str)
                else pd.MultiIndex.from_arrays(
                    [[] for c in index_cols], names=index_cols
                )
            )
            df = pd.DataFrame(pd.DataFrame(columns=cols, index=index))
        else:
            df = pd.DataFrame([item.model_dump() for item in data])

    df.set_index(index_cols, inplace=True)
    return df
