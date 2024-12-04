import pandas as pd
import plotly.graph_objects as go

from .manager import hookspec
from ..backend import Backend
from sqlmodel import Session


@hookspec
def evaluate_results_prepare(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame | pd.Series:
    """
    Evaluates results by adding new columns to the given frame.
    The given data-frame can be directly updated, as each hook implementation receives its own copy.
    The result data-frames will be merged afterwards.
    Given and returned data are/must be indexed first on ``series_id`` and then on ``player_id``.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: a data-frame or series with the respective results
    :return: the given data-frame updated with evaluation data
    """
    raise NotImplementedError("This is just a hook specification")


@hookspec
def evaluate_results_main(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame | pd.Series:
    """
    Evaluates results by adding new columns to the given frame.
    The given data-frame can be directly updated, as each hook implementation receives its own copy.
    The result data-frames will be merged afterwards.
    The given data-frame will include the modifications of ``evaluate_results_prepare`` calls.
    Given and returned data are/must be indexed first on ``series_id`` and then on ``player_id``.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: a data-frame with the respective results
    :return: the given data-frame updated with evaluation data
    """
    raise NotImplementedError("This is just a hook specification")


@hookspec
def evaluate_results_revise(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame | pd.Series:
    """
    Evaluates results by adding new columns to the given frame.
    The given data-frame can be directly updated, as each hook implementation receives its own copy.
    The result data-frames will be merged afterwards.
    The given data-frame will include the modifications of ``evaluate_results_main`` calls.
    Given and returned data are/must be indexed first on ``series_id`` and then on ``player_id``.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: a data-frame with the respective results
    :return: the given data-frame updated with evaluation data
    """
    raise NotImplementedError("This is just a hook specification")


@hookspec
def evaluate_results_total(backend: Backend, session: Session, results: pd.DataFrame) -> pd.DataFrame | pd.Series:
    """
    Aggregate the result evaluation over all series.
    Given data are indexed first on ``series_id`` and then on ``player_id``.
    Returned data must be indexed on ``player_id`` only (``series_id`` has been aggregated).
    The result data-frames will be merged afterwards.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: a data-frame with the respective results
    :return: the given data-frame updated with evaluation data
    """
    raise NotImplementedError("This is just a hook specification")


@hookspec
def plot_results(backend: Backend, session: Session, results: pd.DataFrame) -> go.Figure:
    """
    Create a plot visualizing parts of the results.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: data-frame of evaluated results
    :return: a plotly figure object
    """
    raise NotImplementedError("This is just a hook specification")


@hookspec
def report_results_display(backend: Backend, session: Session, results: pd.DataFrame) -> str:
    """
    Generate HTML code to display result data in the HTML report.

    :param backend: the current backend for acquisition of additional data
    :param session: the current database session for acquisition of additional data
    :param results: data-frame of evaluated results
    :return: a string containing valid HTML code
    """
    raise NotImplementedError("This is just a hook specification")
