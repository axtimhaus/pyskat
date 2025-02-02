from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session

from pyskat.api.app import Dependencies
from pyskat.data_model import Table, TablePublic, TableCreate, TableUpdate, Series, PlayerPublic


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/tables",
        tags=["tables"],
    )

    @router.get("/", response_model=list[TablePublic])
    async def get(session: dependencies.session):
        return session.exec(select(Table)).all()

    @router.get("/{table_id}", response_model=TablePublic)
    async def get_single(table_id: int, session: dependencies.session):
        return session.get(Table, table_id) or raise_not_found(table_id)

    @router.post("/", response_model=TablePublic)
    async def create(table: TableCreate, session: dependencies.session):
        db_table = Table.model_validate(table)

        if db_table.series_id is not None and session.get(Series, db_table.series_id) is None:
            raise HTTPException(status_code=404, detail=f"Series {db_table.series_id} not found")

        session.add(db_table)
        session.commit()
        return db_table

    @router.patch("/{table_id}", response_model=TablePublic)
    async def update(table_id: int, table: TableUpdate, session: dependencies.session):
        db_table = session.get(Table, table_id) or raise_not_found(table_id)

        table_data = table.model_dump(exclude_unset=True)
        db_table.sqlmodel_update(table_data)

        if db_table.series_id is not None and session.get(Series, db_table.series_id) is None:
            raise HTTPException(status_code=404, detail=f"Series {db_table.series_id} not found")

        session.add(db_table)
        session.commit()
        session.refresh(db_table)
        return db_table

    @router.delete("/{table_id}", status_code=204)
    async def delete(table_id: int, session: dependencies.session):
        db_table = session.get(Table, table_id) or raise_not_found(table_id)
        session.delete(db_table)
        session.commit()

    return router


def raise_not_found(table_id: int):
    raise HTTPException(status_code=404, detail=f"Table {table_id} not found")
