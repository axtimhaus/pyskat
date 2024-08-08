from datetime import datetime

from pydantic import BaseModel, Field


class Player(BaseModel):
    id: int = Field(ge=0)
    name: str
    remarks: int = Field(default="")


class Table(BaseModel):
    series_id: int = Field(gt=0)
    table_id: int = Field(gt=0)
    player1_id: int = Field(ge=0)
    player2_id: int = Field(ge=0)
    player3_id: int = Field(ge=0)
    player4_id: int = Field(ge=0)

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
    remarks: int = Field(default="")
    player_ids: list[int]


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
