import pandas as pd
import plotly.graph_objects as go

from .manager import plugin_manager
from . import specs
from . import evaluation
from ..backend import Backend

plugin_manager.add_hookspecs(specs)

plugin_manager.register(evaluation)


def evaluate_results(backend: Backend, series_id: int | None) -> pd.DataFrame:
    if series_id:
        results = backend.results.all_for_series(series_id)
    else:
        results = backend.results.all()

    if not results:
        raise ValueError(f"No results for series {series_id} in database.")

    df = pd.DataFrame([r.model_dump() for r in results])
    df.set_index(["series_id", "player_id"], inplace=True)
    df.sort_index(inplace=True)

    def _remove_input_cols(orig: pd.DataFrame, hook_results: list[pd.DataFrame]):
        return [r.drop(orig.columns, axis=1) for r in hook_results]

    df = df.join(_remove_input_cols(df, plugin_manager.hook.evaluate_results_prepare(backend=backend, results=df)))
    df = df.join(_remove_input_cols(df, plugin_manager.hook.evaluate_results_main(backend=backend, results=df)))
    df = df.join(_remove_input_cols(df, plugin_manager.hook.evaluate_results_revise(backend=backend, results=df)))

    return df


def evaluate_results_total(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=results.index.levels[1])
    return df.join(plugin_manager.hook.evaluate_results_total(backend=backend, results=results))


def create_result_plots(backend: Backend, results: pd.DataFrame) -> list[go.Figure]:
    plots = plugin_manager.hook.plot_results(backend=backend, results=results)
    return plots
