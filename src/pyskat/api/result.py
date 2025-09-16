# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.api.app import Dependencies
from pyskat.data_model import (
    Result,
    ResultPublic,
    ResultCreate,
    ResultUpdate,
    ResultPublicDeep,
)


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/results",
        tags=["results"],
    )

    @router.get("/", response_model=list[ResultPublic])
    async def get(db: dependencies.db):
        return db.exec(select(Result)).all()

    @router.get("/{table_id}/{player_id}", response_model=ResultPublicDeep)
    async def get_single(player_id: int, table_id: int, db: dependencies.db):
        return db.get(
            Result, dict(table_id=table_id, player_id=player_id)
        ) or raise_not_found(table_id, player_id)

    @router.post("/{table_id}/{player_id}", response_model=ResultPublic)
    async def create(
        player_id: int,
        table_id: int,
        result: ResultCreate,
        db: dependencies.db,
    ):
        db_result = Result.model_validate(
            result.model_dump() | dict(table_id=table_id, player_id=player_id)
        )
        db.add(db_result)
        db.commit()
        return db_result

    @router.patch("/{table_id}/{player_id}", response_model=ResultPublic)
    async def update(
        player_id: int,
        table_id: int,
        result: ResultUpdate,
        db: dependencies.db,
    ):
        db_result = db.get(
            Result, dict(table_id=table_id, player_id=player_id)
        ) or raise_not_found(table_id, player_id)
        result_data = result.model_dump(exclude_unset=True)
        db_result.sqlmodel_update(result_data)
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result

    @router.delete("/{table_id}/{player_id}", status_code=204)
    async def delete(player_id: int, table_id: int, db: dependencies.db):
        db_result = db.get(
            Result, dict(table_id=table_id, player_id=player_id)
        ) or raise_not_found(table_id, player_id)
        db.delete(db_result)
        db.commit()

    return router


def raise_not_found(table_id: int, player_id: int):
    raise HTTPException(
        status_code=404,
        detail=f"Result for player {player_id} on table {table_id} not found",
    )
