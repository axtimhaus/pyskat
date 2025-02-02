from fastapi import APIRouter, HTTPException
from sqlmodel import select

from pyskat.api.app import Dependencies
from pyskat.data_model import Series, SeriesPublic, SeriesCreate, SeriesUpdate


def create_router(dependencies: Dependencies) -> APIRouter:
    router = APIRouter(
        prefix="/series",
        tags=["series"],
    )

    @router.get("/", response_model=list[SeriesPublic])
    async def get(session: dependencies.session):
        return session.exec(select(Series)).all()

    @router.get("/{series_id}", response_model=SeriesPublic)
    async def get_single(series_id: int, session: dependencies.session):
        return session.get(Series, series_id) or raise_not_found(series_id)

    @router.post("/", response_model=SeriesPublic)
    async def create(series: SeriesCreate, session: dependencies.session):
        db_series = Series.model_validate(series)
        session.add(db_series)
        session.commit()
        return db_series

    @router.patch("/{series_id}", response_model=SeriesPublic)
    async def update(series_id: int, series: SeriesUpdate, session: dependencies.session):
        db_series = session.get(Series, series_id) or raise_not_found(series_id)
        series_data = series.model_dump(exclude_unset=True)
        db_series.sqlmodel_update(series_data)
        session.add(db_series)
        session.commit()
        session.refresh(db_series)
        return db_series

    @router.delete("/{series_id}", status_code=204)
    async def delete(series_id: int, session: dependencies.session):
        db_series = session.get(Series, series_id) or raise_not_found(series_id)
        session.delete(db_series)
        session.commit()

    return router


def raise_not_found(series_id: int):
    raise HTTPException(status_code=404, detail=f"Series {series_id} not found")
