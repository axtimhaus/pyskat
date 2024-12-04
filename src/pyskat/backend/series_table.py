from datetime import datetime

from .data_model import Series
from sqlmodel import select, Session


class SeriesTable:
    def __init__(self, session: Session):
        self._session = session

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
        self._session.add(series)
        self._session.commit()
        self._session.refresh(series)
        return series

    def update(
        self,
        id: int,
        name: str | None = None,
        date: datetime | None = None,
        remarks: str | None = None,
    ) -> Series:
        """Update an existing series in the database."""
        series = self._session.get(Series, id) or raise_series_not_found(id)

        if name is not None:
            series.name = name

        if date is not None:
            series.date = date

        if remarks is not None:
            series.remarks = remarks

        self._session.add(series)
        self._session.commit()
        self._session.refresh(series)
        return series

    def remove(self, id: int) -> None:
        """Remove a series from the database."""
        series = self._session.get(Series, id) or raise_series_not_found(id)
        self._session.delete(series)
        self._session.commit()

    def get(self, id: int) -> Series:
        """Get a series from the database."""
        series = self._session.get(Series, id)
        return series or raise_series_not_found(id)

    def all(self) -> list[Series]:
        """Get a list of all series in the database."""
        series = self._session.exec(select(Series)).all()
        return list(series)


def raise_series_not_found(id: int):
    raise KeyError(f"A series with the given ID {id} was not found.")
