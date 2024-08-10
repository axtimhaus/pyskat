from datetime import datetime

import numpy as np
import pandas as pd
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
            remarks=remarks or "",
        )
        series.id = self._table.insert(series.model_dump(mode="json", exclude={"id"}))
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
        series = Series(id=id, **updated)

        self._table.update(series.model_dump(mode="json", exclude={"id"}), doc_ids=[id])
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
        """Get a list of all series in the database."""
        result = self._table.all()
        series = [Series(id=r.doc_id, **r) for r in result]
        return series

    def query(self, query: QueryLike) -> list[Series]:
        """Get the results of a TinyDB query."""
        result = self._table.search(query)
        series = [Series(id=r.doc_id, **r) for r in result]
        return series

    def _modify_players(self, series_id: int, action) -> Series:
        original = self._table.get(doc_id=series_id)

        if not original:
            raise_series_not_found(series_id)

        action(original["player_ids"])
        series = Series(id=series_id, **original)
        self._table.update(series.model_dump(mode="json", exclude={"id"}), doc_ids=[series_id])
        return series

    def add_player(self, series_id: int, player_id: int) -> Series:
        """Add a player to a series."""
        return self._modify_players(series_id, lambda ls: ls.append(player_id))

    def remove_player(self, series_id: int, player_id: int) -> Series:
        """Remove a player from a series."""
        return self._modify_players(series_id, lambda ls: ls.remove(player_id))

    def add_players(self, series_id: int, player_ids: list[int]):
        """Add players to a series."""
        return self._modify_players(series_id, lambda ls: ls.extend(player_ids))

    def remove_players(self, series_id: int, player_ids: list[int]):
        """Remove players from a series."""

        def fun(ls: list):
            for i in player_ids:
                ls.remove(i)

        return self._modify_players(series_id, fun)

    def clear_players(self, series_id: int):
        """Remove all players from a series."""
        return self._modify_players(series_id, lambda ls: ls.clear())

    def all_players(self, series_id: int):
        """Remove all players from a series."""

        def fun(ls: list):
            ls.clear()
            players = [p.id for p in self._backend.players.all()]
            ls.extend(players)

        return self._modify_players(series_id, fun)


def raise_series_not_found(id: int):
    raise KeyError(f"A series with the given ID {id} was not found.")
