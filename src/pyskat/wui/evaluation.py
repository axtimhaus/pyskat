import numpy as np
from pydantic import ValidationError

from .helpers import flash_validation_error
from flask import render_template, g, request, Blueprint, abort, redirect, url_for, flash

from ..plugins import evaluate_results, evaluate_results_total, report_content


bp = Blueprint("evaluation", __name__, url_prefix="/evaluation")


@bp.get("/")
def index():
    return render_template(
        "evaluation.html",
        report_content=report_content(g.backend)
    )
