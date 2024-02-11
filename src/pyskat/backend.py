from pathlib import Path
from typing import Optional, Literal

import numpy as np
import pandas as pd
from tinydb import TinyDB, Query
from tinydb.queries import QueryLike

Player = Query()
Result = Query()
Series = Query()
Table = Query()


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

    def remove_player(self, id: int):
        result = self._players.remove(doc_ids=[id])
        if not result:
            raise KeyError("Player with given ID not found.")

    def get_player(self, id: int) -> pd.Series:
        result = self._players.get(doc_id=id)

        if result:
            return pd.Series(result, name=id)

        raise KeyError("Player not found.")

    def query_players(self, query: QueryLike):
        result = self._players.search(query)

        if not result:
            return pd.DataFrame(
                columns=["name", "remarks"], index=pd.Index([], name="id")
            )

        return pd.DataFrame(
            result, index=pd.Index([p.doc_id for p in result], name="id")
        )

    def list_players(self) -> pd.DataFrame:
        players = self._players.all()
        df = pd.DataFrame(
            players, index=pd.Index([p.doc_id for p in players], name="id")
        )
        df.sort_index(inplace=True)
        return df

    def add_result(
        self,
        series_id: int,
        player_id: int,
        points: int,
        won: int,
        lost: int,
        remarks: Optional[str] = None,
    ) -> int:
        result = self._results.search(
            (Result.series_id == series_id) & (Result.player_id == player_id)
        )

        if result:
            raise KeyError(
                "Result with specified series, table and player IDs already exists."
            )

        return self._results.insert(
            dict(
                series_id=series_id,
                player_id=player_id,
                points=points,
                won=won,
                lost=lost,
                remarks=remarks or "",
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
        result = self._results.search(
            (Result.series_id == series_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError(
                "Result with specified series, and player IDs does not exist."
            )

        orig = result[0]

        self._results.update(
            dict(
                series_id=series_id,
                player_id=player_id,
                points=points if points is not None else orig["points"],
                won=won if won is not None else orig["won"],
                lost=lost if lost is not None else orig["won"],
                remarks=remarks if remarks is not None else orig["remarks"],
            ),
            (Result.series_id == series_id) & (Result.player_id == player_id),
        )

    def get_result(self, series_id: int, player_id: int) -> pd.Series:
        result = self._results.search(
            (Result.series_id == series_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError(
                "Result with specified series, table and player IDs does not exist."
            )

        return pd.Series(result[0], name=(series_id, player_id))

    def remove_result(
        self,
        series_id: int,
        player_id: int,
    ) -> None:
        result = self._results.remove(
            (Result.series_id == series_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError(
                "Result with specified series, table and player IDs does not exist."
            )

    def query_results(self, query: QueryLike):
        result = self._results.search(query)

        if not result:
            return pd.DataFrame(
                columns=["points", "won", "lost"],
                index=pd.MultiIndex([[], []], names=["series_id", "player_id"]),
            )

        df = pd.DataFrame(result)
        df.set_index(["series_id", "player_id"], inplace=True)
        return df

    def list_results(self):
        results = self._results.all()
        df = pd.DataFrame(results)
        df.set_index(["series_id", "player_id"], inplace=True)
        df.sort_index(inplace=True)
        return df

    def get_opponents_lost(self, series_id: int, player_id: int):
        table_id = self._tables.get(
            (Table.player_id == player_id) & (Table.series_id == series_id)
        )["table_id"]
        other_players = [
            t["player_id"]
            for t in self._tables.search(
                (Table.player_id != player_id)
                & (Table.series_id == series_id)
                & (Table.table_id == table_id)
            )
        ]
        other_results = self._results.search(
            (Result.series_id == series_id) & (Result.player_id.one_of(other_players))
        )
        df = pd.DataFrame(other_results)

        if len(df) == 0:
            return 0

        return df["lost"].sum()

    def get_table_size(self, series_id: int, player_id: int) -> int:
        table_id = self._tables.get(
            (Table.player_id == player_id) & (Table.series_id == series_id)
        )["table_id"]
        others = self._tables.get(
            (Table.table_id == table_id) & (Table.series_id == series_id)
        )
        return len(others)

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
    ):
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

    def remove_series(self, id: int):
        result = self._series.remove(doc_ids=[id])
        if not result:
            raise KeyError("Series with given ID not found.")

    def get_series(self, id: int) -> pd.Series:
        result = self._series.get(doc_id=id)

        if result:
            return pd.Series(result, name=id)

        raise KeyError("Series with given ID found.")

    def query_series(self, query: QueryLike):
        result = self._series.search(query)

        if not result:
            return pd.DataFrame(
                columns=["name", "date", "remarks"], index=pd.Index([], name="id")
            )

        return pd.DataFrame(
            result, index=pd.Index([p.doc_id for p in result], name="id")
        )

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

    def shuffle_players_to_tables(self, series_id: int) -> pd.DataFrame:
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
        tables = [shuffled[i : i + 4] for i in np.arange(0, player_border, 4)] + [
            shuffled[i : i + 3]
            for i in player_border + np.arange(0, three_player_table_count * 3, 4)
        ]

        concatenated = pd.concat(
            tables,
            keys=range(1, four_player_table_count + three_player_table_count + 1),
            names=["table_id", "player_id"],
        )
        concatenated.reset_index(inplace=True)

        self.clear_tables(series_id)
        for index, row in concatenated.iterrows():
            self.add_table(series_id, row["player_id"], row["table_id"])

        return concatenated

    def list_series(self) -> pd.DataFrame:
        series = self._series.all()
        df = pd.DataFrame(series, index=pd.Index([p.doc_id for p in series], name="id"))
        df.sort_index(inplace=True)
        return df

    def add_table(self, series_id: int, player_id: int, table_id: int) -> int:
        return self._tables.insert(
            dict(series_id=series_id, player_id=player_id, table_id=table_id)
        )

    def remove_table(self, series_id: int, player_id: int):
        result = self._tables.remove(
            (Table.series_id == series_id) & (Table.player_id == player_id)
        )
        if not result:
            raise KeyError("Table with given series and player not found.")

    def clear_tables(self, series_id: int):
        self._tables.remove((Table.series_id == series_id))

    def query_tables(self, query: QueryLike):
        result = self._tables.search(query)

        if not result:
            return pd.DataFrame(
                columns=["table_id"],
                index=pd.MultiIndex([[], []], names=["series_id", "player_id"]),
            )

        df = pd.DataFrame(result)
        df.set_index(["series_id", "player_id"], inplace=True)
        return df

    def list_tables(self, series_id: int = 0) -> pd.DataFrame:
        if series_id == 0:
            result = self._tables.all()
        else:
            result = self._tables.search(Table.series_id == series_id)
        df = pd.DataFrame(result)
        return df
