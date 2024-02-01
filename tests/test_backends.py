import numpy as np

import pandas as pd
import pytest
import tempfile

from pyskat.backend import Backend


@pytest.fixture
def backend(tmp_path):
    backend = Backend(tmp_path / "db.json")

    backend.add_player(1, "P1")
    backend.add_player(3, "P3")
    backend.add_player(7, "P7")
    backend.add_player(6, "P6")
    backend.add_player(4, "P4")
    backend.add_player(2, "P2")
    backend.add_player(5, "P5", "rem")

    backend.add_result(1, 2, 6, 50, 7, 3)
    backend.add_result(1, 1, 3, 450, 5, 1)
    backend.add_result(1, 1, 4, 250, 2, 2)
    backend.add_result(1, 1, 1, 100, 3, 2)
    backend.add_result(1, 2, 5, 700, 3, 1)
    backend.add_result(2, 2, 1, 500, 1, 2)
    backend.add_result(1, 1, 2, 200, 3, 4)
    backend.add_result(1, 2, 7, 350, 2, 1)
    backend.add_result(2, 1, 7, 200, 4, 2)
    backend.add_result(2, 1, 2, 300, 4, 5)
    backend.add_result(2, 2, 3, 730, 9, 4)
    backend.add_result(2, 2, 5, 440, 5, 1)
    backend.add_result(2, 1, 6, 240, 2, 0)
    backend.add_result(2, 2, 4, 100, 2, 0)

    return backend


def test_get_player_by_id(backend: Backend):
    result = backend.get_player(5)

    assert result["name"] == "P5"
    assert result["remarks"] == "rem"

    with pytest.raises(KeyError):
        backend.get_player(42)


def test_list_players(backend: Backend):
    result = backend.list_players()

    assert isinstance(result, pd.DataFrame)
    assert np.all(result.index == range(1, 8))
    assert len(result) == 7


def test_list_results_for_player(backend: Backend):
    result = backend.list_results_for_player(5)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert result.get("player_id", None) is None

    with pytest.raises(KeyError):
        assert backend.list_results_for_player(42)


def test_list_results(backend: Backend):
    result = backend.list_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 14
    assert result.loc[2, 2, 3].points == 730


def test_get_opponents_lost(backend: Backend):
    result = backend.get_opponents_lost(1, 1, 2)
    assert result == 5


def test_evaluate_results(backend: Backend):
    result = backend.evaluate_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 14
    assert np.all(result["won_points"] >= 0)
    assert np.all(np.remainder(result["won_points"], 50) == 0)
    assert np.all(result["lost_points"] <= 0)
    assert np.all(np.remainder(result["lost_points"], 50) == 0)
