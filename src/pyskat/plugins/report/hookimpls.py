from ..manager import hookimpl
from ..evaluation import evaluate_results, evaluate_results_total
from ...backend import Backend
import pandas as pd
import numpy as np
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

THIS_DIR = Path(__file__).parent
ENV = Environment(loader=FileSystemLoader(THIS_DIR / "templates"))

@hookimpl(specname="report_results_display")
def result_table(backend: Backend, results: pd.DataFrame) -> str:
    evaluations = {}

    for ind in results.index.levels[0]:
        if isinstance(ind, int):
            series = backend.series.get(ind)
            title = f"Series {ind} - {series.name}"
        else:
            title = str(ind).title()
        df = results.loc[ind].copy()
        df.reset_index(inplace=True)
        df.sort_values("score", ascending=False, inplace=True)
        df["position"] = np.arange(1, len(df) + 1)
        df.set_index("position", inplace=True)
        evaluations[title] = df

    players=backend.players.all()

    template = ENV.get_template("result_table.html")
    return template.render(
        evaluations=evaluations,
        players={p.id: p for p in players},
    )
