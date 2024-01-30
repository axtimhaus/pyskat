from pathlib import Path
from typing import Optional

import pandas as pd
from tinydb import TinyDB, Query, where

Player = Query()
Result = Query()


class Backend:
    def __init__(self, db_path: Path):
        self.db = TinyDB(db_path)
        self.players = self.db.table("players")
        self.results = self.db.table("results")

    def add_player(self, id: int, name: str, remarks: Optional[str] = None):
        self.players.insert({"id": id, "name": name, "remarks": remarks})

    def get_player_by_id(self, id: int):
        return self.players.search(Player.id == id)[0]

    def get_players_by_name(self, name: str):
        return self.players.search(Player.name == name)

    def add_result(self, series_id: int, table_id: int, player_id: int, points: int, won: int, lost: int,
                   remarks: Optional[str] = None):
        self.results.insert(dict(
            series_id=series_id,
            table_id=table_id,
            player_id=player_id,
            points=points,
            won=won,
            lost=lost,
            remarks=remarks,
        ))

    def list_players(self) -> pd.DataFrame:
        players = self.players.all()
        df = pd.DataFrame(players)
        df.set_index("id", inplace=True)
        df.sort_index(inplace=True)
        return df

    def list_results_for_player(self, player_id: int):
        results = self.results.search(Result.player_id == player_id)
        df = pd.DataFrame(results)
        df.drop("player_id", axis=1, inplace=True)
        df.set_index(["series_id", "table_id"], inplace=True)
        df.sort_index(inplace=True)
        return df

    def list_results(self):
        results = self.results.all()
        df = pd.DataFrame(results)
        df.set_index(["series_id", "table_id", "player_id"], inplace=True)
        df.sort_index(inplace=True)
        return df

    def get_opponents_lost(self, series_id: int, table_id: int, player_id: int):
        other_results = self.results.search(
            (Result.series_id == series_id) & (Result.table_id == table_id) & (Result.player_id != player_id))
        df = pd.DataFrame(other_results)

        if len(df) == 0:
            return 0

        return df["lost"].sum()

    def get_table_size(self, series_id: int, table_id: int):
        return len(self.results.search((Result.series_id == series_id) & (Result.table_id == table_id)))

    def evaluate_results(self):
        results = self.list_results()

        results["won_points"] = results["won"] * 50
        results["lost_points"] = -results["lost"] * 50

        results["table_size"] = [self.get_table_size(s, t) for (s, t, p) in results.index]
        results["opponents_lost"] = [self.get_opponents_lost(s, t, p) for (s, t, p) in results.index]
        results["opponents_lost_points"] = results.apply(
            lambda row: row["opponents_lost"] * (30 if row["table_size"] == 4 else 40),
            axis=1
        )

        return results
