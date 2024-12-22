from sqlmodel import SQLModel, Field

__all__ = ["TablePlayerLink"]


class TablePlayerLink(SQLModel, table=True):
    table_id: int = Field(gt=0, foreign_key="table.id", primary_key=True)
    player_id: int = Field(gt=0, foreign_key="player.id", primary_key=True)
