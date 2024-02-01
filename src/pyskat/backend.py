from pathlib import Path
from typing import Optional

import pandas as pd
from tinydb import TinyDB, Query, where

Player = Query()
Result = Query()


class Backend:
    def __init__(self, db_path: Path):
        self.db = TinyDB(db_path, indent=4)
        self._players = self.db.table("players")
        self._results = self.db.table("results")

    def add_player(self, id: int, name: str, remarks: Optional[str] = None) -> None:
        result = self._players.search(Player.id == id)

        if result:
            raise KeyError("A player with the given ID is already present.")

        self._players.insert(dict(id=id, name=name, remarks=remarks or ""))

    def update_player(self, id: int, name: Optional[str] = None, remarks: Optional[str] = None) -> None:
        result = self._players.search(Player.id == id)

        if not result:
            raise KeyError("A player with the given ID was not found.")

        orig = result[0]

        self._players.update(dict(
            id=id,
            name=name if name is not None else orig["name"],
            remarks=remarks if remarks is not None else orig["remarks"]
        ), Player.id == id)

    def remove_player(self, id: int):
        result = self._players.remove(Player.id == id)
        if not result:
            raise KeyError("Player with given ID not found.")

    def get_player(self, id: int) -> pd.Series:
        result = self._players.search(Player.id == id)

        if result:
            return pd.Series(result[0], name=id)

        raise KeyError("Player not found.")

    def get_players_by_name(self, name: str, exact=True) -> pd.DataFrame:
        if exact:
            result = self._players.search(Player.name == name)
        else:
            result = self._players.search(Player.name.search(name))

        if not result:
            raise KeyError("No player with given name found.")
        return pd.DataFrame(result)

    def add_result(
            self, series_id: int, table_id: int, player_id: int,
            points: int, won: int, lost: int, remarks: Optional[str] = None
    ) -> None:
        result = self._results.search(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id == player_id)
        )

        if result:
            raise KeyError("Result with specified series, table and player IDs already exists.")

        self._results.insert(dict(
            series_id=series_id,
            table_id=table_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks or "",
        ))

    def update_result(
            self, series_id: int, table_id: int, player_id: int,
            points: Optional[int] = None, won: Optional[int] = None,
            lost: Optional[int] = None, remarks: Optional[str] = None
    ) -> None:
        result = self._results.search(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError("Result with specified series, table and player IDs does not exist.")

        orig = result[0]

        self._results.update(dict(
            series_id=series_id,
            table_id=table_id,
            player_id=player_id,
            points=points if points is not None else orig["points"],
            won=won if won is not None else orig["won"],
            lost=lost if lost is not None else orig["won"],
            remarks=remarks if remarks is not None else orig["remarks"],
        ), (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id == player_id))

    def get_result(
            self, series_id: int, table_id: int, player_id: int
    ) -> pd.Series:
        result = self._results.search(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError("Result with specified series, table and player IDs does not exist.")

        return pd.Series(result[0], name=(series_id, table_id, player_id))

    def remove_result(
            self, series_id: int, table_id: int, player_id: int,
    ) -> None:
        result = self._results.remove(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id == player_id)
        )

        if not result:
            raise KeyError("Result with specified series, table and player IDs does not exist.")

    def list_players(self) -> pd.DataFrame:
        players = self._players.all()
        df = pd.DataFrame(players)
        df.set_index("id", inplace=True)
        df.sort_index(inplace=True)
        return df

    def list_results_for_player(self, player_id: int):
        results = self._results.search(Result.player_id == player_id)
        df = pd.DataFrame(results)
        df.drop("player_id", axis=1, inplace=True)
        df.set_index(["series_id", "table_id"], inplace=True)
        df.sort_index(inplace=True)
        return df

    def list_results(self):
        results = self._results.all()
        df = pd.DataFrame(results)
        df.set_index(["series_id", "table_id", "player_id"], inplace=True)
        df.sort_index(inplace=True)
        return df

    def get_opponents_lost(self, series_id: int, table_id: int, player_id: int):
        other_results = self._results.search(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id != player_id))
        df = pd.DataFrame(other_results)

        if len(df) == 0:
            return 0

        return df["lost"].sum()

    def get_table_size(self, series_id: int, table_id: int) -> int:
        return len(self._results.search((Result.series_id == series_id) & (Result.table_id == table_id)))

    def evaluate_results(self) -> pd.DataFrame:
        results = self.list_results()

        results["won_points"] = results["won"] * 50
        results["lost_points"] = -results["lost"] * 50

        results["table_size"] = [self.get_table_size(s, t) for (s, t, p) in results.index]
        results["opponents_lost"] = [self.get_opponents_lost(s, t, p) for (s, t, p) in results.index]

        def calc_opponents_lost_points(row):
            if row["table_size"] == 4:
                return row["opponents_lost"] * 30
            if row["table_size"] == 3:
                return row["opponents_lost"] * 40
            raise ValueError(f"Table size can only be 3 or 4, but was {row['table_size']}.")

        results["opponents_lost_points"] = results.apply(calc_opponents_lost_points, axis=1)

        return results
