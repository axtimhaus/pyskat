from pathlib import Path
from typing import Optional, Literal

import numpy as np
import pandas as pd
from tinydb import TinyDB, Query
from tinydb.table import Document
from tinydb.queries import QueryLike

Player = Query()
Result = Query()
Series = Query()
Table = Query()


def _players_to_dataframe(players: list[Document]):
    if not players:
        return pd.DataFrame(columns=["name", "remarks"], index=pd.Index([], name="id"))

    df = pd.DataFrame(players, index=pd.Index([p.doc_id for p in players], name="id"))
    df.sort_index(inplace=True)
    return df


def _results_to_dataframe(results: list[Document]):
    if not results:
        return pd.DataFrame(
            columns=["points", "won", "lost"],
            index=pd.MultiIndex([[], []], names=["series_id", "player_id"]),
        )

    df = pd.DataFrame(results)
    df.set_index(["series_id", "player_id"], inplace=True)
    df.sort_index(inplace=True)
    return df


def _series_to_dataframe(series: list[Document]):
    if not series:
        return pd.DataFrame(
            columns=["name", "date", "remarks"], index=pd.Index([], name="id")
        )

    df = pd.DataFrame(series, index=pd.Index([p.doc_id for p in series], name="id"))
    df.sort_index(inplace=True)
    return df


def _tables_to_dataframe(tables: list[Document]):
    if not tables:
        return pd.DataFrame(
            columns=["players"],
            index=pd.MultiIndex([[], []], names=["series_id", "table_id"]),
        )

    df = pd.DataFrame(tables)
    df.set_index(["series_id", "table_id"], inplace=True)
    df.sort_index(inplace=True)
    return df


RESULT_ID_MODULE = 1000
TABLE_ID_MODULE = 1000


def _make_result_id(
    series_id: int | list[int], player_id: int | list[int]
) -> int | list[int]:
    return np.array(series_id) * RESULT_ID_MODULE + np.array(player_id)


def _make_table_id(
    series_id: int | list[int], player_id: int | list[int]
) -> int | list[int]:
    return np.array(series_id) * TABLE_ID_MODULE + np.array(player_id)


class Backend:
    def __init__(self, database_file: Path):
        self._db = TinyDB(database_file, indent=4)

        self._players = self._db.table("players")
        """Table of players."""

        self._results = self._db.table("results")
        """Table of game results."""

        self._series = self._db.table("series")
        """Table of game series."""

        self._tables = self._db.table("tables")
        """Table of series-player-table mappings."""

    def add_player(self, name: str, remarks: Optional[str] = None) -> int:
        return self._players.insert(dict(name=name, remarks=remarks or ""))

    def update_player(
        self, id: int, name: Optional[str] = None, remarks: Optional[str] = None
    ) -> None:
        orig = self._players.get(doc_id=id)

        if not orig:
            raise KeyError("A player with the given ID was not found.")

        self._players.update(
            dict(
                name=name if name is not None else orig["name"],
                remarks=remarks if remarks is not None else orig["remarks"],
            ),
            doc_ids=[id],
        )

    def remove_player(self, id: int) -> None:
        result = self._players.remove(doc_ids=[id])
        if not result:
            raise KeyError("Player with given ID not found.")

    def get_player(self, id: int) -> dict[str, ...]:
        result = self._players.get(doc_id=id)

        if result:
            result["id"] = id
            return result

        raise KeyError("Player not found.")

    def query_players(self, query: QueryLike) -> pd.DataFrame:
        players = self._players.search(query)
        return _players_to_dataframe(players)

    def list_players(self) -> pd.DataFrame:
        players = self._players.all()
        return _players_to_dataframe(players)

    def add_result(
        self,
        series_id: int,
        player_id: int,
        points: int,
        won: int,
        lost: int,
        remarks: Optional[str] = None,
    ) -> int:
        doc_id = _make_result_id(series_id, player_id)
        result = self._results.get(doc_id=doc_id)

        if result:
            raise KeyError(
                "Result with specified series, table and player IDs already exists."
            )

        return self._results.insert(
            Document(
                dict(
                    series_id=series_id,
                    player_id=player_id,
                    points=points,
                    won=won,
                    lost=lost,
                    remarks=remarks or "",
                ),
                doc_id,
            )
        )

    def update_result(
        self,
        series_id: int,
        player_id: int,
        points: Optional[int] = None,
        won: Optional[int] = None,
        lost: Optional[int] = None,
        remarks: Optional[str] = None,
    ) -> None:
        doc_id = _make_result_id(series_id, player_id)
        result = self._results.get(doc_id=doc_id)

        if not result:
            raise KeyError(
                "Result with specified series, and player IDs does not exist."
            )

        orig = result

        self._results.update(
            dict(
                points=points if points is not None else orig["points"],
                won=won if won is not None else orig["won"],
                lost=lost if lost is not None else orig["won"],
                remarks=remarks if remarks is not None else orig["remarks"],
            ),
            doc_ids=[doc_id],
        )

    def get_result(self, series_id: int, player_id: int) -> dict[str, ...]:
        result = self._results.get(doc_id=_make_result_id(series_id, player_id))

        if not result:
            raise KeyError(
                "Result with specified series, table and player IDs does not exist."
            )

        return result

    def remove_result(
        self,
        series_id: int,
        player_id: int,
    ) -> None:
        result = self._results.remove(doc_ids=[_make_result_id(series_id, player_id)])

        if not result:
            raise KeyError(
                "Result with specified series, table and player IDs does not exist."
            )

    def query_results(self, query: QueryLike):
        results = self._results.search(query)
        return _results_to_dataframe(results)

    def list_results(self):
        results = self._results.all()
        return _results_to_dataframe(results)

    def get_opponents_lost(self, series_id: int, player_id: int) -> int:
        table = self.get_table_with_player(series_id, player_id)
        other_players = list(table["players"])
        other_players.remove(player_id)
        other_results = self._results.get(
            doc_ids=_make_result_id(series_id, other_players)
        )
        df = pd.DataFrame(other_results)

        if len(df) == 0:
            return 0

        return df["lost"].sum()

    def get_table_with_player(self, series_id: int, player_id: int) -> dict[str, ...]:
        table = self._tables.get(
            (Table.series_id == series_id)
            & (Table.players.test(lambda t: player_id in t))
        )

        if not table:
            raise KeyError("No table with this player in this series.")

        return table

    def get_table_size(self, series_id: int, player_id: int) -> int:
        return len(self.get_table_with_player(series_id, player_id)["players"])

    def evaluate_results(self) -> pd.DataFrame:
        results = self.list_results()

        results["won_points"] = results["won"] * 50
        results["lost_points"] = -results["lost"] * 50

        results["table_size"] = [self.get_table_size(s, p) for (s, p) in results.index]
        results["opponents_lost"] = [
            self.get_opponents_lost(s, p) for (s, p) in results.index
        ]

        def calc_opponents_lost_points(row):
            if row["table_size"] == 4:
                return row["opponents_lost"] * 30
            if row["table_size"] == 3:
                return row["opponents_lost"] * 40
            raise ValueError(
                f"Table size can only be 3 or 4, but was {row['table_size']}."
            )

        results["opponents_lost_points"] = results.apply(
            calc_opponents_lost_points, axis=1
        )

        results["score"] = (
            results["points"]
            + results["won_points"]
            + results["lost_points"]
            + results["opponents_lost_points"]
        )
        results.drop(["remarks"], axis=1, inplace=True)

        return results

    def evaluate_total(self) -> pd.DataFrame:
        results = self.evaluate_results()

        sums = results.groupby("player_id").sum()
        sums.drop(["table_size"], axis=1, inplace=True)

        results.reset_index(inplace=True)
        pivoted = results.pivot(index="player_id", columns="series_id").swaplevel(
            axis=1
        )
        series = [pivoted[s] for s in pivoted.columns.levels[0]]
        concatenated = pd.concat(
            [*series, sums], axis=1, keys=[*pivoted.columns.levels[0], "total"]
        )

        return concatenated

    def add_series(self, name: str, date: Optional[str], remarks: Optional[str]) -> int:
        return self._series.insert(
            dict(name=name, date=date or "", remarks=remarks or "", players=[])
        )

    def update_series(
        self,
        id: int,
        name: Optional[str] = None,
        date: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> None:
        orig = self._series.get(doc_id=id)

        if not orig:
            raise KeyError("A series with the given ID was not found.")

        self._series.update(
            dict(
                name=name if name is not None else orig["name"],
                date=date if date is not None else orig["date"],
                remarks=remarks if remarks is not None else orig["remarks"],
            ),
            doc_ids=[id],
        )

    def remove_series(self, id: int) -> None:
        result = self._series.remove(doc_ids=[id])
        if not result:
            raise KeyError("Series with given ID not found.")

    def get_series(self, id: int) -> dict[str, ...]:
        result = self._series.get(doc_id=id)

        if result:
            result["id"] = id
            return result

        raise KeyError("Series with given ID found.")

    def query_series(self, query: QueryLike) -> pd.DataFrame:
        series = self._series.search(query)
        return _series_to_dataframe(series)

    def add_players_to_series(self, id: int, players: list[int] | Literal["all"]):
        if not self._series.contains(doc_id=id):
            raise KeyError("Series not found.")

        if players == "all":
            all_players = [p.doc_id for p in self._players.all()]
            self._series.update(dict(players=all_players), doc_ids=[id])
        else:
            old_players = self._series.get(doc_id=id)["players"]
            players = set(old_players).union(players)
            self._series.update(dict(players=list(players)), doc_ids=[id])

    def remove_players_from_series(self, id: int, players: list[int] | Literal["all"]):
        if not self._series.contains(doc_id=id):
            raise KeyError("Series not found.")

        if players == "all":
            self._series.update(dict(players=[]), doc_ids=[id])
        else:
            old_players = self._series.get(doc_id=id)["players"]
            players = set(old_players).difference(players)
            self._series.update(dict(players=list(players)), doc_ids=[id])

    def shuffle_players_to_tables(self, series_id: int):
        player_ids = self._series.get(doc_id=series_id)["players"]

        if not player_ids:
            raise ValueError("This series has no players assigned.")

        players = pd.DataFrame(self._players.get(doc_ids=player_ids), index=player_ids)
        shuffled = players.sample(frac=1)

        player_count = len(shuffled)
        div, mod = divmod(player_count, 4)
        three_player_table_count = 4 - mod
        four_player_table_count = div + 1 - three_player_table_count

        player_border = four_player_table_count * 4
        tables = [shuffled[i : i + 4].index for i in np.arange(0, player_border, 4)] + [
            shuffled[i : i + 3].index
            for i in player_border + np.arange(0, three_player_table_count * 3, 4)
        ]

        self.clear_tables(series_id)
        for i, ps in enumerate(tables, 1):
            self.add_table(series_id, i, list(ps))

    def list_series(self) -> pd.DataFrame:
        series = self._series.all()
        return _series_to_dataframe(series)

    def add_table(self, series_id: int, table_id: int, player_ids: list[int]) -> int:
        if not (3 <= len(player_ids) <= 4):
            raise ValueError("Table size can only be 3 or 4.")

        return self._tables.insert(
            Document(
                dict(series_id=series_id, table_id=table_id, players=player_ids),
                doc_id=_make_table_id(series_id, table_id),
            )
        )

    def get_table(self, series_id: int, table_id: int) -> dict[str, ...]:
        result = self._tables.get(doc_id=_make_table_id(series_id, table_id))

        if not result:
            raise KeyError("Table with specified ID in series not found.")

        return result

    def remove_table(self, series_id: int, table_id: int) -> None:
        result = self._tables.remove(doc_ids=[_make_table_id(series_id, table_id)])
        if not result:
            raise KeyError("Table with given ID and in series not found.")

    def clear_tables(self, series_id: int) -> None:
        self._tables.remove((Table.series_id == series_id))

    def query_tables(self, query: QueryLike):
        tables = self._tables.search(query)
        return _tables_to_dataframe(tables)

    def list_tables(self, series_id: int = 0) -> pd.DataFrame:
        if series_id == 0:
            tables = self._tables.all()
        else:
            tables = self._tables.search(Table.series_id == series_id)

        return _tables_to_dataframe(tables)
