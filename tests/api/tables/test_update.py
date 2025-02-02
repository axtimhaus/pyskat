import pytest
from faker import Faker
from fastapi.testclient import TestClient

def add_table(client: TestClient, faker: Faker):
    for i in range(1, 6):
        name = faker.name()
        client.post("/players", json={"name": name})

    remarks = faker.word()
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
        "remarks": remarks,
    })
    assert res.status_code == 200
    return res.json()


def test_remarks(client, faker):
    created_table = add_table(client, faker)
    new_remarks = faker.word()

    res = client.patch(f"/tables/{created_table['id']}", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == created_table | {"remarks": new_remarks}


def test_non_existent(client, faker):
    res = client.patch(f"/tables/{984379843}", json={})
    assert res.status_code == 404

@pytest.mark.parametrize("place", [1, 2, 3, 4])
def test_players(client, faker, place:int):
    created_table = add_table(client, faker)
    res = client.patch(f"/tables/{created_table['id']}", json={f"player{place}_id": 5})
    assert res.status_code == 200
    assert res.json() == created_table | {f"player{place}_id": 5}

@pytest.mark.parametrize("place", [1, 2, 3, 4])
def test_players_non_existent(client, faker, place:int):
    created_table = add_table(client, faker)
    res = client.patch(f"/tables/{created_table['id']}", json={f"player{place}_id": 965387})
    assert res.status_code == 404


def test_series_existing(client, faker):
    created_table = add_table(client, faker)
    client.post("/series", json={"date": faker.date_time().isoformat()})
    res = client.patch(f"/tables/{created_table['id']}", json={"series_id": 1})
    assert res.status_code == 200
    assert res.json() == created_table | {"series_id": 1}


def test_series_non_existing(client, faker):
    created_table = add_table(client, faker)
    res = client.patch(f"/tables/{created_table['id']}", json={"series_id": 8798324})
    assert res.status_code == 404
