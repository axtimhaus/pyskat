import pandas as pd
import plotly.graph_objects as go

from .manager import hookspec
from ..backend import Backend


@hookspec
def evaluate_results_prepare(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates results by adding new columns to the given frame.
    The given data frame can be directly updated, as each hook implementation receives its own copy.
    The result data frames will be merged afterwards.

    :param backend: the current backend for acquisition of additional data
    :param results: a data frame with the respective results
    :return: the given data frame updated with evaluation data
    """


@hookspec
def evaluate_results_main(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates results by adding new columns to the given frame.
    The given data frame can be directly updated, as each hook implementation receives its own copy.
    The result data frames will be merged afterwards.
    The given data frame will include the modifications of ``evaluate_results_prepare`` calls.

    :param backend: the current backend for acquisition of additional data
    :param results: a data frame with the respective results
    :return: the given data frame updated with evaluation data
    """


@hookspec
def evaluate_results_revise(backend: Backend, results: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates results by adding new columns to the given frame.
    The given data frame can be directly updated, as each hook implementation receives its own copy.
    The result data frames will be merged afterwards.
    The given data frame will include the modifications of ``evaluate_results_main`` calls.

    :param backend: the current backend for acquisition of additional data
    :param results: a data frame with the respective results
    :return: the given data frame updated with evaluation data
    """


@hookspec
def plot_results(backend: Backend, results: pd.DataFrame) -> go.Figure:
    """
    Create a plot visualizing parts of the results.

    :param backend: the current backend for acquisition of additional data
    :param results: data frame of evaluated results
    :return: a plotly figure object
    """
