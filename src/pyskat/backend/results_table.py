import pandas as pd
from tinydb.queries import QueryLike, Query
from tinydb.table import Document

from .backend import Backend
from .data_model import TableResult, Table
from .helpers import update_if_not_none


class TableResultsTable:
    def __init__(self, backend: Backend, id_module=1000):
        self._backend = backend
        self._table = self._backend.db.table("results")
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
            series_id=series_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks or "",
        )

        id = self.make_id(series_id, player_id)

        if self._table.contains(doc_id=id):
            raise KeyError(f"Result for series {series_id} and player {player_id} already present.")

        self._table.insert(Document(result.model_dump(mode="json"), id))
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
            raise_result_not_found(series_id, player_id)

        updated = update_if_not_none(
            original,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        )
        result = TableResult(**updated)

        self._table.update(result.model_dump(mode="json"), doc_ids=[id])
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
            raise_result_not_found(series_id, player_id)

    def get(
        self,
        series_id: int,
        player_id: int,
    ) -> TableResult:
        """Get a result from the database."""
        id = self.make_id(series_id, player_id)
        result = self._table.get(doc_id=id)

        if not result:
            raise_result_not_found(series_id, player_id)

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

    def all_for_series(self, series_id: int) -> list[Table]:
        """Get all the results for a defined series in the database."""
        results = self._table.search(Query().series_id == series_id)
        results = [Table(id=p.doc_id, **p) for p in results]
        return results

    def clear_for_series(self, series_id: int) -> None:
        """Remove all the results for a defined series in the database."""
        self._table.remove(Query().series_id == series_id)

    def get_opponents_lost(self, series_id: int, player_id: int) -> int:
        table = self._backend.tables.get_table_with_player(series_id, player_id)
        other_players = table.player_ids
        other_players.remove(player_id)
        others_lost = [self.get(series_id, p).lost for p in other_players]

        return sum(others_lost)


def raise_result_not_found(series_id: int, player_id: int):
    raise KeyError(f"A result with the given ID {series_id}/{player_id} was not found.")
