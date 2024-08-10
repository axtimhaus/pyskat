import pandas as pd

from pyskat.backend import Backend


def evaluate_results(backend: Backend) -> pd.DataFrame:
    results = backend.results.all()

    if not results:
        raise ValueError("No results in database.")

    df = pd.DataFrame([r.model_dump() for r in results])
    df.set_index(["series_id", "player_id"], inplace=True)
    df.sort_index(inplace=True)

    df["won_points"] = df["won"] * 50
    df["lost_points"] = -df["lost"] * 50

    df["table_size"] = df.apply(lambda row: backend.tables.get_table_with_player(*row.name).size, axis=1)

    df["opponents_lost"] = df.apply(lambda row: backend.results.get_opponents_lost(*row.name), axis=1)

    def calc_opponents_lost_points(row):
        if row["table_size"] == 4:
            return row["opponents_lost"] * 30
        if row["table_size"] == 3:
            return row["opponents_lost"] * 40
        raise ValueError(f"Table size can only be 3 or 4, but was {row['table_size']}.")

    df["opponents_lost_points"] = df.apply(calc_opponents_lost_points, axis=1)

    df["score"] = df["points"] + df["won_points"] + df["lost_points"] + df["opponents_lost_points"]

    return df


def evaluate_total(backend: Backend) -> pd.DataFrame:
    results = evaluate_results(backend)

    sums = results.groupby("player_id").sum()
    sums.drop(["table_size"], axis=1, inplace=True)

    results.reset_index(inplace=True)
    pivoted = results.pivot(index="player_id", columns="series_id").swaplevel(axis=1)
    series = [pivoted[s] for s in pivoted.columns.levels[0]]
    concatenated = pd.concat([*series, sums], axis=1, keys=[*pivoted.columns.levels[0], "total"])

    return concatenated
