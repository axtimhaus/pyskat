from datetime import datetime

from tinydb.queries import QueryLike

from .backend import Backend
from .data_model import Series
from .helpers import update_if_not_none


class SeriesTable:
    def __init__(self, backend: Backend):
        self._backend = backend
        self._table = self._backend.db.table("series")

    def add(
        self,
        name: str,
        date: datetime,
        player_ids: list[int] | None = None,
        remarks: str | None = None,
    ) -> Series:
        """Add a new series to the database."""
        series = Series(
            id=0,
            name=name,
            date=date,
            player_ids=player_ids or [],
            remarks=remarks,
        )
        series.id = self._table.insert(series.model_dump())
        return series

    def update(
        self,
        id: int,
        name: str | None = None,
        date: datetime | None = None,
        player_ids: list[int] | None = None,
        remarks: str | None = None,
    ) -> Series:
        """Update an existing series in the database."""
        original = self._table.get(doc_id=id)

        if not original:
            raise_series_not_found(id)

        updated = update_if_not_none(
            original,
            name=name,
            date=date,
            player_ids=player_ids,
            remarks=remarks,
        )
        series = Series(**updated)

        self._table.update(series.model_dump(), doc_ids=[id])
        return series

    def remove(self, id: int) -> None:
        """Remove a series from the database."""
        result = self._table.remove(doc_ids=[id])
        if not result:
            raise_series_not_found(id)

    def get(self, id: int) -> Series:
        """Get a series from the database."""
        result = self._table.get(doc_id=id)

        if not result:
            raise_series_not_found(id)

        series = Series(id=id, **result)
        return series

    def all(self) -> list[Series]:
        """Get a list of all seriess in the database."""
        result = self._table.all()
        series = [Series(id=r.doc_id, **r) for r in result]
        return series

    def query(self, query: QueryLike) -> list[Series]:
        """Get the results of a TinyDB query."""
        result = self._table.search(query)
        series = [Series(id=r.doc_id, **r) for r in result]
        return series


def raise_series_not_found(id: int):
    raise KeyError(f"A series with the given ID {id} was not found.")
