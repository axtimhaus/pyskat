from ..manager import plugin_manager
from . import hookimpls
from ...backend import Backend
from ..evaluation import evaluate_results, evaluate_results_total
import pandas as pd
from .jinja_config import ENV

plugin_manager.register(hookimpls)


def report_standalone(backend: Backend):
    return ENV.get_template("main.html").render(report_content=report_content(backend))


def report_content(backend: Backend):
    series_evaluation = evaluate_results(backend, None)
    total_evaluation = evaluate_results_total(backend, series_evaluation)
    concatenated = pd.concat(
        [series_evaluation, pd.concat([total_evaluation], keys=["total"])]
    )
    return "\n".join(
        plugin_manager.hook.report_results_display(
            backend=backend, results=concatenated
        )
    )
