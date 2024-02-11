import numpy as np

import pandas as pd
import pytest
import tempfile

from pyskat.backend import Backend, Player, Table


@pytest.fixture
def backend(tmp_path):
    backend = Backend(tmp_path / "db.json")

    backend.add_player("P1")
    backend.add_player("P2")
    backend.add_player("P3")
    backend.add_player("P4")
    backend.add_player("P5", "rem")
    backend.add_player("P6")
    backend.add_player("P7")

    backend.add_result(1, 6, 50, 7, 3)
    backend.add_result(1, 3, 450, 5, 1)
    backend.add_result(1, 4, 250, 2, 2)
    backend.add_result(1, 1, 100, 3, 2)
    backend.add_result(1, 5, 700, 3, 1)
    backend.add_result(2, 1, 500, 1, 2)
    backend.add_result(1, 2, 200, 3, 4)
    backend.add_result(1, 7, 350, 2, 1)
    backend.add_result(2, 7, 200, 4, 2)
    backend.add_result(2, 2, 300, 4, 5)
    backend.add_result(2, 3, 730, 9, 4)
    backend.add_result(2, 5, 440, 5, 1)
    backend.add_result(2, 6, 240, 2, 0)
    backend.add_result(2, 4, 100, 2, 0)

    backend.add_table(1, 1, [2, 4, 6, 7])
    backend.add_table(1, 2, [1, 3, 5])
    backend.add_table(2, 1, [1, 3, 4, 7])
    backend.add_table(2, 2, [2, 5, 6])

    backend.add_series("Nr1", "2024-02-04", "")
    backend.add_series("Nr2", "2024-02-05", "")

    return backend


def test_get_player(backend: Backend):
    result = backend.get_player(5)

    assert result.name == 5
    assert result["name"] == "P5"
    assert result["remarks"] == "rem"

    with pytest.raises(KeyError):
        backend.get_player(42)


def test_update_player(backend: Backend):
    with pytest.raises(KeyError):
        backend.update_player(634)

    backend.update_player(1, "new")
    assert backend.get_player(1)["name"] == "new"

    backend.update_player(1, remarks="rem")
    assert backend.get_player(1)["name"] == "new"
    assert backend.get_player(1)["remarks"] == "rem"


def test_remove_player(backend: Backend):
    with pytest.raises(KeyError):
        backend.remove_player(42)
    backend.remove_player(1)

    with pytest.raises(KeyError):
        backend.get_player(1)


def test_query_players(backend: Backend):
    result = backend.query_players(Player.name == "P5").iloc[0]
    assert result.name == 5

    result = backend.query_players(Player.name.search("P"))
    assert len(result) == 7

    result = backend.query_players(Player.name == "abc")
    assert len(result) == 0
    assert result.index.name == "id"
    assert all(result.columns == ["name", "remarks"])


def test_get_result(backend: Backend):
    result = backend.get_result(1, 6)

    assert result["points"] == 50
    assert result["won"] == 7
    assert result["lost"] == 3


def test_update_result(backend: Backend):
    with pytest.raises(KeyError):
        backend.add_result(1, 6, 100, 1, 1)

    backend.update_result(1, 6, 150)
    assert backend.get_result(1, 6)["points"] == 150

    backend.update_result(1, 6, won=1)
    assert backend.get_result(1, 6)["points"] == 150
    assert backend.get_result(1, 6)["won"] == 1


def test_remove_result(backend: Backend):
    with pytest.raises(KeyError):
        backend.remove_result(1, 15)
    backend.remove_result(1, 6)

    with pytest.raises(KeyError):
        backend.get_result(1, 6)


def test_list_players(backend: Backend):
    result = backend.list_players()

    assert isinstance(result, pd.DataFrame)
    assert np.all(result.index == range(1, 8))
    assert len(result) == 7


def test_list_results(backend: Backend):
    result = backend.list_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 14
    assert result.loc[2, 3].points == 730


def test_get_opponents_lost(backend: Backend):
    result = backend.get_opponents_lost(1, 2)
    assert result == 6


def test_evaluate_results(backend: Backend):
    result = backend.evaluate_results()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 14
    assert np.all(result["won_points"] >= 0)
    assert np.all(np.remainder(result["won_points"], 50) == 0)
    assert np.all(result["lost_points"] <= 0)
    assert np.all(np.remainder(result["lost_points"], 50) == 0)


def test_evaluate_total(backend: Backend):
    result = backend.evaluate_total()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 7
    assert np.all(result["total", "won_points"] >= 0)
    assert np.all(np.remainder(result["total", "won_points"], 50) == 0)
    assert np.all(result["total", "lost_points"] <= 0)
    assert np.all(np.remainder(result["total", "lost_points"], 50) == 0)


def test_shuffle_players_to_tables(backend: Backend):
    with pytest.raises(ValueError):
        backend.shuffle_players_to_tables(1)

    backend.add_players_to_series(1, "all")
    backend.shuffle_players_to_tables(1)

    assert len(backend.get_table(1, 1)["players"]) == 4
    assert len(backend.get_table(1, 2)["players"]) == 3

    assert len(backend.list_tables(1)) == 2


def test_update_series(backend: Backend):
    backend.update_series(1, name="abc")
    assert backend.get_series(1)["name"] == "abc"
    assert backend.get_series(1)["date"] == "2024-02-04"

    backend.update_series(1, date="today")
    assert backend.get_series(1)["name"] == "abc"
    assert backend.get_series(1)["date"] == "today"


def test_remove_series(backend: Backend):
    with pytest.raises(KeyError):
        backend.remove_series(42)
    backend.remove_series(1)

    with pytest.raises(KeyError):
        backend.get_series(1)


def test_add_players_to_series_all(backend: Backend):
    backend.add_players_to_series(1, "all")

    series = backend.get_series(1)
    assert series["players"] == list(range(1, 8))


def test_add_players_to_series_ids(backend: Backend):
    backend.add_players_to_series(1, [1, 4, 6])

    series = backend.get_series(1)
    assert series["players"] == [1, 4, 6]
