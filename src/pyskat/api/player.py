# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.api.app import Dependencies
from pyskat.data_model import (
    Player,
    PlayerPublic,
    PlayerCreate,
    PlayerUpdate,
    PlayerPublicDeep,
)


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/player",
        tags=["player"],
    )

    @router.get("/", response_model=list[PlayerPublic])
    async def get(db: dependencies.db):
        return db.exec(select(Player)).all()

    @router.get("/{player_id}", response_model=PlayerPublicDeep)
    async def get_single(player_id: int, db: dependencies.db):
        return db.get(Player, player_id) or raise_not_found(player_id)

    @router.post("/", response_model=PlayerPublic)
    def create(player: PlayerCreate, db: dependencies.db):
        db_player = Player.model_validate(player)
        db.add(db_player)
        db.commit()
        return db_player

    @router.patch("/{player_id}", response_model=PlayerPublic)
    async def update(player_id: int, player: PlayerUpdate, db: dependencies.db):
        db_player = db.get(Player, player_id) or raise_not_found(player_id)
        player_data = player.model_dump(exclude_unset=True)
        db_player.sqlmodel_update(player_data)
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
        return db_player

    @router.delete("/{player_id}", status_code=204)
    async def delete(player_id: int, db: dependencies.db):
        db_player = db.get(Player, player_id) or raise_not_found(player_id)
        db.delete(db_player)
        db.commit()

    return router


def raise_not_found(player_id: int):
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
