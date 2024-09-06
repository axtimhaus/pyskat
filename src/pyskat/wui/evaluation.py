import numpy as np
from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

from ..plugins import evaluate_results, evaluate_results_total

bp = Blueprint("evaluation", __name__, url_prefix="/evaluation")


@bp.get("/")
def index():
    evaluations = {}

    try:
        evaluation = evaluate_results(g.backend, None)
        for ind in evaluation.index.levels[0]:
            series = g.backend.series.get(ind)
            title = f"Series {ind} - {series.name}"
            df = evaluation.loc[ind].copy()
            df.reset_index(inplace=True)
            df.sort_values("score", ascending=False, inplace=True)
            df["position"] = np.arange(1, len(df) + 1)
            df.set_index("position", inplace=True)
            evaluations[title] = df

        total = evaluate_results_total(g.backend, evaluation)
        total.reset_index(inplace=True)
        total.sort_values("score", ascending=False, inplace=True)
        total["position"] = np.arange(1, len(total) + 1)
        total.set_index("position", inplace=True)
        evaluations["Total"] = total
    except KeyError:
        flash("Incomplete result data.", "danger")


    players=g.backend.players.all()

    return render_template(
        "evaluation.html",
        evaluations=evaluations,
        players={p.id: p for p in players},
    )
