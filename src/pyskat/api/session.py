# pyright: reportInvalidTypeForm=false

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.api.app import Dependencies
from pyskat.data_model import Session, SessionPublic, SessionCreate, SessionUpdate


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/session",
        tags=["session"],
    )

    @router.get("/", response_model=list[SessionPublic])
    async def get(db: dependencies.db):
        return db.exec(select(Session)).all()

    @router.get("/{session_id}", response_model=SessionPublic)
    async def get_single(session_id: int, db: dependencies.db):
        return db.get(Session, session_id) or raise_not_found(session_id)

    @router.post("/", response_model=SessionPublic)
    async def create(session: SessionCreate, db: dependencies.db):
        db_session = Session.model_validate(session)
        db.add(db_session)
        db.commit()
        return db_session

    @router.patch("/{session_id}", response_model=SessionPublic)
    async def update(session_id: int, session: SessionUpdate, db: dependencies.db):
        db_session = db.get(Session, session_id) or raise_not_found(session_id)
        session_data = session.model_dump(exclude_unset=True)
        db_session.sqlmodel_update(session_data)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @router.delete("/{session_id}", status_code=204)
    async def delete(session_id: int, db: dependencies.db):
        db_session = db.get(Session, session_id) or raise_not_found(session_id)
        db.delete(db_session)
        db.commit()

    return router


def raise_not_found(session_id: int):
    raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
