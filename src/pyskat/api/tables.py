from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session

from pyskat.api.app import Dependencies
from pyskat.data_model import Table, TablePublic, TableCreate, TableUpdate, Series, PlayerPublic, Player

def check_links(session: Session, table: Table):
    if table.series_id is not None and session.get(Series, table.series_id) is None:
        raise HTTPException(status_code=404, detail=f"Series {table.series_id} not found")

    if session.get(Player, table.player1_id) is None:
        raise HTTPException(status_code=404, detail=f"Player {table.player1_id} not found")

    if session.get(Player, table.player2_id) is None:
        raise HTTPException(status_code=404, detail=f"Player {table.player2_id} not found")

    if session.get(Player, table.player3_id) is None:
        raise HTTPException(status_code=404, detail=f"Player {table.player3_id} not found")

    if table.player4_id is not None and session.get(Player, table.player4_id) is None:
        raise HTTPException(status_code=404, detail=f"Player {table.player4_id} not found")


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
        check_links(session, db_table)
        session.add(db_table)
        session.commit()
        return db_table

    @router.patch("/{table_id}", response_model=TablePublic)
    async def update(table_id: int, table: TableUpdate, session: dependencies.session):
        db_table = session.get(Table, table_id) or raise_not_found(table_id)
        table_data = table.model_dump(exclude_unset=True)
        db_table.sqlmodel_update(table_data)
        check_links(session, db_table)
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
