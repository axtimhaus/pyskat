from ..backend import Backend
from .manager import plugin_manager, hookimpl
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from sqlmodel import Session


def create_result_plots(backend: Backend, session: Session, results: pd.DataFrame) -> list[go.Figure]:
    plots = plugin_manager.hook.plot_results(backend=backend, session=session, results=results)
    return plots


@hookimpl(specname="plot_results")
def plot_total_scores_hist(backend: Backend, results: pd.DataFrame):
    df = results.loc["total"].sort_values("score")
    df.reset_index(inplace=True)
    df["player_label"] = df["player_name"].str.cat([f" ({i})" for i in df["player_id"]])
    fig = px.bar(df, x="player_label", y="score")
    fig.update_layout(title="Total Player Scores")
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Score")
    return fig


@hookimpl(specname="plot_results")
def plot_points_sources(backend: Backend, results: pd.DataFrame):
    df = (
        results.loc[
            "total",
            ["points", "won_points", "lost_points", "opponents_lost_points"],
        ]
        .agg("sum")
        .apply("abs")
    ) / results.loc["total", "score"].sum()
    fig = px.bar(df, y=0)
    fig.update_layout(title="Fractions of Points in the Total Scores")
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Fraction of Score")
    return fig
