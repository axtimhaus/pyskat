from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.api.app import Dependencies
from pyskat.data_model import Player, PlayerPublic, PlayerCreate, PlayerUpdate


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/players",
        tags=["players"],
    )

    @router.get("/", response_model=list[PlayerPublic])
    async def get(session: dependencies.session):
        return session.exec(select(Player)).all()

    @router.get("/{id}", response_model=PlayerPublic)
    async def get_single(id: int, session: dependencies.session):
        player = session.get(Player, id)
        if not player:
            raise HTTPException(status_code=404, detail=f"Player {id} not found")

    @router.post("/", response_model=PlayerPublic)
    async def create(player: PlayerCreate, session: dependencies.session):
        db_player = Player.model_validate(player)
        session.add(db_player)
        session.commit()
        return db_player

    @router.patch("/{id}", response_model=PlayerPublic)
    async def update(id: int, player: PlayerUpdate, session: dependencies.session):
        db_player = session.get(Player, id)
        if not db_player:
            raise HTTPException(status_code=404, detail=f"Player {id} not found")
        player_data = player.model_dump(exclude_unset=True)
        db_player.sqlmodel_update(player_data)
        session.add(db_player)
        session.commit()
        session.refresh(db_player)
        return db_player

    @router.delete("/{id}", status_code=204)
    async def delete(id: int, session: dependencies.session):
        db_player = session.get(Player, id)
        if not db_player:
            raise HTTPException(status_code=404, detail=f"Player {id} not found")
        session.delete(db_player)
        session.commit()

    return router
