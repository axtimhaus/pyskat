import numpy as np
from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

from ..plugins import evaluate_results

bp = Blueprint("evaluation", __name__, url_prefix="/evaluation")


@bp.get("/")
def index():
    evaluations = {}

    try:
        evaluation = evaluate_results(g.backend, None)
        for ind in evaluation.index.levels[0]:
            if isinstance(ind, int):
                series = g.backend.series.get(ind)
                title = f"Series {ind} - {series.name}"
            elif isinstance(ind, str):
                title = ind.title()
            else:
                title = None

            df = evaluation.loc[ind].copy()
            df.sort_values("score", ascending=False, inplace=True)
            df["position"] = np.arange(1, len(df) + 1)
            df.reset_index(inplace=True)
            df.set_index("position", inplace=True)
            evaluations[title] = df
    except KeyError:
        flash("Incomplete result data.", "danger")

    players=g.backend.players.all()

    return render_template(
        "evaluation.html",
        evaluations=evaluations,
        players={p.id: p for p in players},
    )
