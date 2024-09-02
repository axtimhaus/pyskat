import numpy as np
import pandas as pd
from tinydb.queries import Query, QueryLike
from tinydb.table import Document

from .backend import Backend
from .data_model import Table, Player, to_pandas
from .helpers import update_if_not_none


class TablesTable:
    def __init__(self, backend: Backend):
        self._backend = backend
        self._db = self._backend.db

    def get_table(self, series_id):
        return self._db.table(f"series_{series_id}_tables")

    def add(
        self,
        series_id: int,
        player1_id: int,
        player2_id: int,
        player3_id: int,
        player4_id: int = 0,
        remarks: str | None = None or "",
    ) -> Table:
        """Add a new table to the database."""
        table = self.get_table(series_id)

        model = Table(
            series_id=series_id,
            table_id=None,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )

        table.insert(model.model_dump(mode="json", exclude={"table_id", "series_id"}))
        return model

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
        table = self.get_table(series_id)
        original = table.get(doc_id=table_id)

        if not original:
            raise_table_not_found(series_id, table_id)

        updated = update_if_not_none(
            original,
            player1_id=player1_id,
            player2_id=player2_id,
            player3_id=player3_id,
            player4_id=player4_id,
            remarks=remarks,
        )
        model = Table(series_id=series_id, table_id=table_id, **updated)

        table.update(model.model_dump(mode="json", exclude={"table_id", "series_id"}), doc_ids=[table_id])
        return table

    def remove(
        self,
        series_id: int,
        table_id: int,
    ) -> None:
        """Remove a table from the database."""
        table = self.get_table(series_id)
        result = table.remove(doc_ids=[table_id])
        if not result:
            raise_table_not_found(series_id, table_id)

    def get(
        self,
        series_id: int,
        table_id: int,
    ) -> Table:
        """Get a table from the database."""
        table = self.get_table(series_id)
        result = table.get(doc_id=table_id)

        if not result:
            raise_table_not_found(series_id, table_id)

        result = Table(series_id=series_id, table_id=table_id, **result)
        return result

    def query(self, series_id: int, query: QueryLike) -> list[Table]:
        """Get the tables of a TinyDB query."""
        table = self.get_table(series_id)
        result = table.search(query)
        tables = [Table(series_id=series_id, table_id=p.doc_id, **p) for p in result]
        return tables

    def all(self, series_id: int) -> list[Table]:
        """Get all the tables for a defined series in the database."""
        table = self.get_table(series_id)
        tables = table.all()
        tables = [Table(series_id=series_id, table_id=p.doc_id, **p) for p in tables]
        return tables

    def clear_for_series(self, series_id: int) -> None:
        """Remove all the tables for a defined series in the database."""
        self.get_table(series_id).truncate()

    def shuffle_players_for_series(
        self,
        series_id: int,
        active_only: bool = True,
        include: list[int] | None = None,
        include_only: list[int] | None = None,
        exclude: list[int] | None = None,
    ):
        players = to_pandas(self._backend.players.all(), Player, "id")

        if include_only is not None:
            selector = players.index.isin(include_only)
        else:
            selector = np.full(len(players.index), True)

            if active_only:
                selector = selector & players.active

            if include:
                selector = selector | players.index.isin(include)

            if exclude:
                selector = selector & np.logical_not(players.index.isin(exclude))

        shuffled = players[selector].sample(frac=1)

        player_count = len(shuffled)
        div, mod = divmod(player_count, 4)
        if mod == 0:
            three_player_table_count = 0
            four_player_table_count = div
        else:
            three_player_table_count = 4 - mod
            four_player_table_count = div + 1 - three_player_table_count

        player_border = four_player_table_count * 4
        tables = [shuffled[i : i + 4] for i in np.arange(0, player_border, 4)] + [
            shuffled[i : i + 3] for i in player_border + np.arange(0, three_player_table_count * 3, 3)
        ]

        self.clear_for_series(series_id)
        for i, ps in enumerate(tables, 1):
            self.add(series_id, *ps.index)

    def get_table_with_player(self, series_id: int, player_id: int) -> Table:
        q = Query()
        table = self.get_table(series_id).get(
            (q.player1_id == player_id)
            | (q.player2_id == player_id)
            | (q.player3_id == player_id)
            | (q.player4_id == player_id)
        )

        if not table:
            raise ValueError(f"A table with player {player_id} is not present in series {series_id}.")

        return Table(**table)


def raise_table_not_found(series_id: int, table_id: int):
    raise KeyError(f"A table with the given IDs {series_id}/{table_id} was not found.")
