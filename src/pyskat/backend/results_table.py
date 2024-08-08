from typing import TYPE_CHECKING

from tinydb.queries import QueryLike
from tinydb.table import Document

from .data_model import TableResult
from .helpers import update_if_not_none

if TYPE_CHECKING:
    from .database import Database


class TableResultsTable:
    def __init__(self, db: "Database", id_module=1000):
        self._db = db
        self._table = self._db.db.table("results")
        self.id_module = id_module

    def make_id(
        self,
        series_id: int,
        player_id: int,
    ):
        return series_id * self.id_module + player_id

    def add(
        self,
        series_id: int,
        player_id: int,
        points: int,
        won: int,
        lost: int,
        remarks: str | None = None,
    ) -> TableResult:
        """Add a new result to the database."""
        result = TableResult(
            id=self.make_id(series_id, player_id),
            series_id=series_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
        self._table.insert(Document(result.model_dump(), result.id))
        return result

    def update(
        self,
        series_id: int,
        player_id: int,
        points: int | None = None,
        won: int | None = None,
        lost: int | None = None,
        remarks: str | None = None,
    ) -> TableResult:
        """Update an existing result in the database."""
        id = self.make_id(series_id, player_id)
        original = self._table.get(doc_id=id)

        if not original:
            raise_result_not_found(id)

        updated = update_if_not_none(
            original,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
        result = TableResult(**updated)

        self._table.update(result.model_dump(), doc_ids=[id])
        return result

    def remove(
        self,
        series_id: int,
        player_id: int,
    ) -> None:
        """Remove a result from the database."""
        id = self.make_id(series_id, player_id)
        result = self._table.remove(doc_ids=[id])
        if not result:
            raise_result_not_found(id)

    def get(
        self,
        series_id: int,
        player_id: int,
    ) -> TableResult:
        """Get a result from the database."""
        id = self.make_id(series_id, player_id)
        result = self._table.get(doc_id=id)

        if not result:
            raise_result_not_found(id)

        result = TableResult(id=id, **result)
        return result

    def all(self) -> list[TableResult]:
        """Get a list of all results in the database."""
        result = self._table.all()
        results = [TableResult(id=p.doc_id, **p) for p in result]
        return results

    def query(self, query: QueryLike) -> list[TableResult]:
        """Get the results of a TinyDB query."""
        result = self._table.search(query)
        results = [TableResult(id=p.doc_id, **p) for p in result]
        return results


def raise_result_not_found(id: int):
    raise KeyError(f"A result with the given ID {id} was not found.")
