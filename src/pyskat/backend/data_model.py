from datetime import datetime
from typing import Iterable

import pandas as pd
from pydantic import BaseModel, Field


class Player(BaseModel):
    id: int = Field(ge=0)
    name: str
    active: bool = Field(default=True)
    remarks: str = Field(default="")


class Table(BaseModel):
    series_id: int = Field(gt=0)
    table_id: int = Field(gt=0)
    player1_id: int = Field(ge=0)
    player2_id: int = Field(ge=0)
    player3_id: int = Field(ge=0)
    player4_id: int = Field(ge=0)
    remarks: str = Field(default="")

    @property
    def player_ids(self) -> list[int]:
        players = [self.player1_id, self.player2_id, self.player3_id, self.player4_id]

        while True:
            try:
                players.remove(0)
            except ValueError:
                break

        return players

    @property
    def size(self) -> int:
        return len(self.player_ids)


class Series(BaseModel):
    id: int = Field(ge=0)
    name: str = Field(default="")
    date: datetime
    remarks: str = Field(default="")


class TableResult(BaseModel):
    series_id: int = Field(gt=0)
    player_id: int = Field(gt=0)
    points: int
    won: int = Field(ge=0)
    lost: int = Field(ge=0)
    remarks: str = Field(default="")


class TableEvaluation(TableResult):
    won_points: int = Field(ge=0)
    lost_points: int = Field(le=0)
    opponents_lost: int = Field(ge=0)
    opponents_lost_points: int = Field(ge=0)
    score: int


class TotalResult:
    player_id: int = Field(gt=0)
    series_scores: list[int]
    total_score: int


def to_pandas(
    data: BaseModel | Iterable[BaseModel], model_type: type[BaseModel], index_cols: str | list[str]
) -> pd.DataFrame:
    if isinstance(data, BaseModel):
        df = pd.DataFrame[data.model_dump()]
    else:
        if not data:
            cols = list(model_type.model_fields.keys())
            index = (
                pd.Index([], name=index_cols)
                if isinstance(index_cols, str)
                else pd.MultiIndex.from_arrays([[] for c in index_cols], names=index_cols)
            )
            df = pd.DataFrame(pd.DataFrame(columns=cols, index=index))
        else:
            df = pd.DataFrame([item.model_dump() for item in data])

    df.set_index(index_cols, inplace=True)
    return df
