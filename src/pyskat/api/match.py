# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session

from pyskat.api.app import Dependencies
from pyskat.data_model import (
    Match,
    MatchPublic,
    MatchCreate,
    MatchUpdate,
    Session,
    PlayerPublic,
    Player,
)


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/matches",
        tags=["matches"],
    )

    @router.get("/", response_model=list[MatchPublic])
    async def get(db: dependencies.db):
        return db.exec(select(Match)).all()

    @router.get("/{match_id}", response_model=MatchPublic)
    async def get_single(match_id: int, db: dependencies.db):
        return db.get(Match, match_id) or raise_not_found(match_id)

    @router.post("/", response_model=MatchPublic)
    async def create(match: MatchCreate, db: dependencies.db):
        db_match = Match.model_validate(match)
        db.add(db_match)
        db.commit()
        return db_match

    @router.patch("/{match_id}", response_model=MatchPublic)
    async def update(match_id: int, match: MatchUpdate, db: dependencies.db):
        db_match = db.get(Match, match_id) or raise_not_found(match_id)
        match_data = match.model_dump(exclude_unset=True)
        db_match.sqlmodel_update(match_data)
        db.add(db_match)
        db.commit()
        db.refresh(db_match)
        return db_match

    @router.delete("/{match_id}", status_code=204)
    async def delete(match_id: int, db: dependencies.db):
        db_match = db.get(Match, match_id) or raise_not_found(match_id)
        db.delete(db_match)
        db.commit()

    return router


def raise_not_found(match_id: int):
    raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
