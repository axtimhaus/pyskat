import pandas as pd

from .manager import hookimpl
from ..backend import Backend
from .manager import plugin_manager
from sqlmodel import Session


def evaluate_results(backend: Backend, session: Session, series_id: int | None) -> pd.DataFrame:
    if series_id:
        results = backend.results(session).all_for_series(series_id)
    else:
        results = backend.results(session).all()

    if not results:
        raise ValueError(f"No results for series {series_id} in database.")

    df = pd.DataFrame([r.model_dump() for r in results])
    df.set_index(["series_id", "player_id"], inplace=True)
    df.sort_index(inplace=True)

    def _remove_input_cols(orig: pd.DataFrame, hook_results: list[pd.DataFrame]):
        return [r.drop(orig.columns, axis=1) for r in hook_results]

    df = df.join(
        _remove_input_cols(
            df, plugin_manager.hook.evaluate_results_prepare(backend=backend, session=session, results=df)
        )
    )
    df = df.join(
        _remove_input_cols(df, plugin_manager.hook.evaluate_results_main(backend=backend, session=session, results=df))
    )
    df = df.join(
        _remove_input_cols(
            df, plugin_manager.hook.evaluate_results_revise(backend=backend, session=session, results=df)
        )
    )

    return df


def evaluate_results_total(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=results.index.levels[1])
    return df.join(plugin_manager.hook.evaluate_results_total(backend=backend, session=session, results=results))


@hookimpl(specname="evaluate_results_prepare")
def determine_table_size(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame:
    results["table_size"] = results.apply(
        lambda row: backend.tables(session).get_table_with_player(*row.name).size, axis=1
    )
    return results


@hookimpl(specname="evaluate_results_main")
def evaluate_points(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame:
    results["won_points"] = results["won"] * 50
    results["lost_points"] = -results["lost"] * 50

    results["opponents_lost"] = results.apply(
        lambda row: backend.results(session).get_opponents_lost(*row.name), axis=1
    )

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


@hookimpl(specname="evaluate_results_revise")
def add_player_names(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame:
    results["player_name"] = results.apply(lambda row: backend.players(session).get(row.name[1]).name, axis=1)
    return results


@hookimpl(specname="evaluate_results_total")
def total_points_and_score(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    total = (
        results.loc[
            :,
            ["points", "won", "won_points", "lost", "lost_points", "opponents_lost", "opponents_lost_points", "score"],
        ]
        .groupby("player_id")
        .agg("sum")
    )
    return total


@hookimpl(specname="evaluate_results_total")
def total_player_names(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame | pd.Series:
    return pd.Series(
        [backend.players(session).get(p).name for p in results.index.levels[1]],
        index=results.index.levels[1],
        name="player_name",
    )
