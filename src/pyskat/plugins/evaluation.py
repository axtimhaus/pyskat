import pandas as pd

from .manager import hookimpl
from ..backend import Backend


@hookimpl(specname="evaluate_results_prepare")
def determine_table_size(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    results["table_size"] = results.apply(lambda row: backend.tables.get_table_with_player(*row.name).size, axis=1)
    return results


@hookimpl(specname="evaluate_results_main")
def evaluate_points(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    results["won_points"] = results["won"] * 50
    results["lost_points"] = -results["lost"] * 50

    results["opponents_lost"] = results.apply(lambda row: backend.results.get_opponents_lost(*row.name), axis=1)

    def calc_opponents_lost_points(row):
        if row["table_size"] == 4:
            return row["opponents_lost"] * 30
        if row["table_size"] == 3:
            return row["opponents_lost"] * 40
        raise ValueError(f"Table size can only be 3 or 4, but was {row['table_size']}.")

    results["opponents_lost_points"] = results.apply(calc_opponents_lost_points, axis=1)
    return results


@hookimpl(specname="evaluate_results_revise")
def sum_score(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    results["score"] = (
        results["points"] + results["won_points"] + results["lost_points"] + results["opponents_lost_points"]
    )
    return results
