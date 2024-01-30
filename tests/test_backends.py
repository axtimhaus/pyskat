import numpy as np

import pandas as pd
import pytest
import tempfile

from pyskat.backend import Backend


@pytest.fixture
def backend(tmp_path):
    backend = Backend(tmp_path / "db.json")

    backend.add_player(21, "Max")
    backend.add_player(42, "Paul", "rem")
    backend.add_player(1, "Lars", "rem")

    backend.add_result(1, 1, 21, 100, 3, 2)
    backend.add_result(2, 1, 21, 200, 4, 0)
    backend.add_result(3, 1, 21, 300, 5, 2)
    backend.add_result(1, 1, 42, 200, 3, 1)
    backend.add_result(1, 1, 1, 50, 2, 1)

    return backend


def test_get_player_by_id(backend: Backend):
    result = backend.get_player_by_id(42)

    assert result["name"] == "Paul"
    assert result["remarks"] == "rem"


def test_list_players(backend: Backend):
    result = backend.list_players()

    assert isinstance(result, pd.DataFrame)
    assert np.all(result.index == [1, 21, 42])
    assert len(result) == 3


def test_list_results_for_player(backend: Backend):
    result = backend.list_results_for_player(21)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert result.get("player_id", None) is None


def test_list_results(backend: Backend):
    result = backend.list_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5
    assert result.loc[1, 1, 42].points == 200


def test_get_opponents_lost(backend: Backend):
    result = backend.get_opponents_lost(1, 1, 21)
    assert result == 2


def test_evaluate_results(backend: Backend):
    result = backend.evaluate_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5
    assert np.all(result["won_points"] >= 0)
    assert np.all(np.remainder(result["won_points"], 50) == 0)
    assert np.all(result["lost_points"] <= 0)
    assert np.all(np.remainder(result["lost_points"], 50) == 0)
