from .manager import plugin_manager
from . import specs
from . import evaluation
from . import plots
from .evaluation import evaluate_results, evaluate_results_total
from .report import report_content, report_standalone

plugin_manager.add_hookspecs(specs)
plugin_manager.register(evaluation)
plugin_manager.register(plots)
