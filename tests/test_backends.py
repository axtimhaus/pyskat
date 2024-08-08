from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from tinydb import Query

from pyskat.backend import Backend
from pyskat.backend.evaluation import evaluate_results, evaluate_total


@pytest.fixture
def backend(tmp_path):
    backend = Backend(tmp_path / "db.json")

    backend.players.add("P1")
    backend.players.add("P2")
    backend.players.add("P3")
    backend.players.add("P4")
    backend.players.add("P5", "rem")
    backend.players.add("P6")
    backend.players.add("P7")

    backend.results.add(1, 6, 50, 7, 3)
    backend.results.add(1, 3, 450, 5, 1)
    backend.results.add(1, 4, 250, 2, 2)
    backend.results.add(1, 1, 100, 3, 2)
    backend.results.add(1, 5, 700, 3, 1)
    backend.results.add(2, 1, 500, 1, 2)
    backend.results.add(1, 2, 200, 3, 4)
    backend.results.add(1, 7, 350, 2, 1)
    backend.results.add(2, 7, 200, 4, 2)
    backend.results.add(2, 2, 300, 4, 5)
    backend.results.add(2, 3, 730, 9, 4)
    backend.results.add(2, 5, 440, 5, 1)
    backend.results.add(2, 6, 240, 2, 0)
    backend.results.add(2, 4, 100, 2, 0)

    backend.tables.add(1, 1, 2, 4, 6, 7)
    backend.tables.add(1, 2, 1, 3, 5)
    backend.tables.add(2, 1, 1, 3, 4, 7)
    backend.tables.add(2, 2, 2, 5, 6)

    backend.series.add("Nr1", "2024-02-04", "")
    backend.series.add("Nr2", "2024-02-05", "")

    return backend


def test_get_player(backend: Backend):
    result = backend.players.get(5)

    assert result.id == 5
    assert result.name == "P5"
    assert result.remarks == "rem"

    with pytest.raises(KeyError):
        backend.players.get(42)


def test_update_player(backend: Backend):
    with pytest.raises(KeyError):
        backend.players.update(634)

    backend.players.update(1, "new")
    assert backend.players.get(1).name == "new"

    backend.players.update(1, remarks="rem")
    assert backend.players.get(1).name == "new"
    assert backend.players.get(1).remarks == "rem"


def test_remove_player(backend: Backend):
    with pytest.raises(KeyError):
        backend.players.remove(42)
    backend.players.remove(1)

    with pytest.raises(KeyError):
        backend.players.get(1)


def test_query_players(backend: Backend):
    q = Query()
    result = backend.players.query(q.name == "P5")[0]
    assert result.id == 5

    result = backend.players.query(q.name.search("P"))
    assert len(result) == 7

    result = backend.players.query(q.name == "abc")
    assert len(result) == 0


def test_get_result(backend: Backend):
    result = backend.results.get(1, 6)

    assert result.points == 50
    assert result.won == 7
    assert result.lost == 3


def test_update_result(backend: Backend):
    with pytest.raises(KeyError):
        backend.results.add(1, 6, 100, 1, 1)

    backend.results.update(1, 6, 150)
    assert backend.results.get(1, 6).points == 150

    backend.results.update(1, 6, won=1)
    assert backend.results.get(1, 6).points == 150
    assert backend.results.get(1, 6).won == 1


def test_remove_result(backend: Backend):
    with pytest.raises(KeyError):
        backend.results.remove(1, 15)
    backend.results.remove(1, 6)

    with pytest.raises(KeyError):
        backend.results.get(1, 6)


def test_list_players(backend: Backend):
    result = backend.players.all()

    assert len(result) == 7


def test_list_results(backend: Backend):
    result = backend.results.all()

    assert len(result) == 14


def test_get_opponents_lost(backend: Backend):
    result = backend.results.get_opponents_lost(1, 2)
    assert result == 6


def test_evaluate_results(backend: Backend):
    result = evaluate_results(backend)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 14
    assert np.all(result["won_points"] >= 0)
    assert np.all(np.remainder(result["won_points"], 50) == 0)
    assert np.all(result["lost_points"] <= 0)
    assert np.all(np.remainder(result["lost_points"], 50) == 0)


def test_evaluate_total(backend: Backend):
    result = evaluate_total(backend)

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
    backend.series.update(1, name="abc")
    assert backend.series.get(1).name == "abc"
    assert backend.series.get(1).date == datetime.fromisoformat("2024-02-04")

    today = datetime.today()
    backend.series.update(1, date=today)
    assert backend.series.get(1).name == "abc"
    assert backend.series.get(1).date == today


def test_remove_series(backend: Backend):
    with pytest.raises(KeyError):
        backend.series.remove(42)
    backend.series.remove(1)

    with pytest.raises(KeyError):
        backend.series.get(1)


def test_add_players_to_series_all(backend: Backend):
    backend.series.all_players(1)
    series = backend.series.get(1)
    assert series.player_ids == list(range(1, 8))

    backend.series.clear_players(1)
    series = backend.series.get(1)
    assert series.player_ids == list()


def test_add_players_to_series_ids(backend: Backend):
    backend.series.add_players(1, [1, 4, 6])
    series = backend.series.get(1)
    assert series.player_ids == [1, 4, 6]

    backend.series.remove_players(1, [4, 6])
    series = backend.series.get(1)
    assert series.player_ids == [1]

def test_add_players_to_series_single(backend: Backend):
    backend.series.add_player(1, 1)
    series = backend.series.get(1)
    assert series.player_ids == [1]

    backend.series.add_player(1, 4)
    series = backend.series.get(1)
    assert series.player_ids == [1, 4]

    backend.series.remove_player(1, 1)
    series = backend.series.get(1)
    assert series.player_ids == [4]
