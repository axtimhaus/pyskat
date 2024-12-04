from ..manager import hookimpl
from ..evaluation import evaluate_results, evaluate_results_total
from ..plots import create_result_plots
from ...backend import Backend
import pandas as pd
import numpy as np
from .jinja_config import ENV


@hookimpl(specname="report_results_display")
def result_table(backend: Backend, results: pd.DataFrame) -> str:
    with backend.get_session() as session:
        evaluations = {}

        for ind in results.index.levels[0]:
            if isinstance(ind, int):
                series = backend.series(session).get(ind)
                title = f"Series {ind} - {series.name}"
            else:
                title = str(ind).title()
            df = results.loc[ind].copy()
            df.reset_index(inplace=True)
            df.sort_values("score", ascending=False, inplace=True)
            df["position"] = np.arange(1, len(df) + 1)
            df.set_index("position", inplace=True)
            evaluations[title] = df

        players = backend.players(session).all()

        template = ENV.get_template("result_table.html")
        return template.render(
            evaluations=evaluations,
            players={p.id: p for p in players},
        )


@hookimpl(specname="report_results_display")
def plots(backend: Backend, results: pd.DataFrame) -> str:
    with backend.get_session() as session:
        plots = create_result_plots(backend, session, results)
        template = ENV.get_template("plots.html")
        plot_titles = [p.layout.title.text for p in plots]

        for p in plots:
            p.update_layout(
                title=None,
                template="simple_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                modebar=dict(bgcolor="rgba(0, 0, 0, 0)"),
            )
        plots_html = [p.to_html() for p in plots]
        return template.render(plots=plots_html, plot_titles=plot_titles, zip=zip)
