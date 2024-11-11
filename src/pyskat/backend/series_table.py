from datetime import datetime

from .backend import Backend
from .data_model import Series
from sqlmodel import select


class SeriesTable:
    def __init__(self, backend: Backend):
        self._backend = backend

    def add(
        self,
        name: str,
        date: datetime,
        remarks: str | None = None,
    ) -> Series:
        """Add a new series to the database."""
        series = Series(
            name=name,
            date=date,
            remarks=remarks or "",
        )
        with self._backend.get_session() as session:
            session.add(series)
            session.commit()
            session.refresh(series)
            return series

    def update(
        self,
        id: int,
        name: str | None = None,
        date: datetime | None = None,
        remarks: str | None = None,
    ) -> Series:
        """Update an existing series in the database."""
        with self._backend.get_session() as session:
            series = session.get(Series, id) or raise_series_not_found(id)

            if name is not None:
                series.name = name

            if date is not None:
                series.date = date

            if remarks is not None:
                series.remarks = remarks

            session.add(series)
            session.commit()
            session.refresh(series)
            return series

    def remove(self, id: int) -> None:
        """Remove a series from the database."""
        with self._backend.get_session() as session:
            series = session.get(Series, id) or raise_series_not_found(id)
            session.delete(series)
            session.commit()

    def get(self, id: int) -> Series:
        """Get a series from the database."""
        with self._backend.get_session() as session:
            series = session.get(Series, id)
            return series or raise_series_not_found(id)

    def all(self) -> list[Series]:
        """Get a list of all series in the database."""
        with self._backend.get_session() as session:
            series = session.exec(select(Series)).all()
            return list(series)


def raise_series_not_found(id: int):
    raise KeyError(f"A series with the given ID {id} was not found.")
