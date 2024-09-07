from ..backend import Backend
from .manager import plugin_manager
import plotly.graph_objects as go
import pandas as pd

def create_result_plots(backend: Backend, results: pd.DataFrame) -> list[go.Figure]:
    plots = plugin_manager.hook.plot_results(backend=backend, results=results)
    return plots
