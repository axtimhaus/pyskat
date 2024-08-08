from typing import TYPE_CHECKING

from tinydb.queries import QueryLike
from tinydb.table import Document

from .data_model import Table
from .helpers import update_if_not_none

if TYPE_CHECKING:
    from .database import Database


class TablesTable:
    def __init__(self, db: "Database", id_module=1000):
        self._db = db
        self._table = self._db.db.table("tables")
        self.id_module = id_module

    def make_id(
        self,
        series_id: int,
        table_id: int,
    ):
        return series_id * self.id_module + table_id

    def add(
        self,
        series_id: int,
        table_id: int,
        player1_id: int,
        player2_id: int,
        player3_id: int,
        player4_id: int,
        remarks: str | None = None,
    ) -> Table:
        """Add a new table to the database."""
        table = Table(
            id=self.make_id(series_id, table_id),
            series_id=series_id,
            table_id=table_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )
        self._table.insert(Document(table.model_dump(), table.id))
        return table

    def update(
        self,
        series_id: int,
        table_id: int,
        player1_id: int | None = None,
        player2_id: int | None = None,
        player3_id: int | None = None,
        player4_id: int | None = None,
        remarks: str | None = None,
    ) -> Table:
        """Update an existing table in the database."""
        id = self.make_id(series_id, table_id)
        original = self._table.get(doc_id=id)

        if not original:
            raise_table_not_found(id)

        updated = update_if_not_none(
            original,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )
        table = Table(**updated)

        self._table.update(table.model_dump(), doc_ids=[id])
        return table

    def remove(
        self,
        series_id: int,
        table_id: int,
    ) -> None:
        """Remove a table from the database."""
        id = self.make_id(series_id, table_id)
        table = self._table.remove(doc_ids=[id])
        if not table:
            raise_table_not_found(id)

    def get(
        self,
        series_id: int,
        table_id: int,
    ) -> Table:
        """Get a table from the database."""
        id = self.make_id(series_id, table_id)
        table = self._table.get(doc_id=id)

        if not table:
            raise_table_not_found(id)

        table = Table(id=id, **table)
        return table

    def all(self) -> list[Table]:
        """Get a list of all tables in the database."""
        table = self._table.all()
        tables = [Table(id=p.doc_id, **p) for p in table]
        return tables

    def query(self, query: QueryLike) -> list[Table]:
        """Get the tables of a TinyDB query."""
        table = self._table.search(query)
        tables = [Table(id=p.doc_id, **p) for p in table]
        return tables


def raise_table_not_found(id: int):
    raise KeyError(f"A table with the given ID {id} was not found.")
