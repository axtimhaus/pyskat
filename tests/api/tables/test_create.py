import pytest
from faker import Faker
from rich.pretty import pprint
from fastapi.testclient import TestClient


def test_3player(client, faker, add_players):
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
    })
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 3,
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": None,
        "series_id": None,
        "remarks": "",
    }


def test_4player(client, faker, add_players):
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
    })
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "series_id": None,
        "remarks": "",
    }

@pytest.mark.parametrize("place", [1,2,3,4])
def test_player_non_existent(client, faker, add_players, place:int):
    create_data={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
    }
    create_data[f"player{place}_id"] = 9834795834
    res = client.post("/tables", json=create_data)
    pprint(res.json())
    assert res.status_code == 404


def test_remarks(client, faker, add_players):
    remarks = faker.word()

    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "remarks": remarks,
    })
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "series_id": None,
        "remarks": remarks,
    }


def test_series_existing(client, faker, add_players):
    client.post("/series", json={"date": faker.date_time().isoformat()})
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "series_id": 1,
    })
    pprint(res.json())
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 4,
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "series_id": 1,
        "remarks": "",
    }


def test_series_non_existing(client, faker, add_players):
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "series_id": 43594579345,
    })
    pprint(res.json())
    assert res.status_code == 404


def test_multiple(client, faker, add_players):
    for i in range(1, 5):
        remarks = faker.word()

        res = client.post("/tables", json={
            "player1_id": 1,
            "player2_id": 2,
            "player3_id": 3,
            "player4_id": 4,
            "remarks": remarks,
        })
        pprint(res.json())
        assert res.status_code == 200
        assert res.json() == {
            "id": i,
            "size": 4,
            "player1_id": 1,
            "player2_id": 2,
            "player3_id": 3,
            "player4_id": 4,
            "series_id": None,
            "remarks": remarks,
        }
