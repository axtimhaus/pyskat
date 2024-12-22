from faker import Faker
from fastapi.testclient import TestClient


def add_players(client: TestClient, faker: Faker):
    for i in range(1, 5):
        name = faker.name()
        active = faker.boolean()
        remarks = faker.word()

        res = client.post("/players", json={"name": name, "active": active, "remarks": remarks})
        assert res.status_code == 200
        yield {
            "id": i,
            "name": name,
            "active": active,
            "remarks": remarks,
        }


def test_all(client, faker):
    created_players = list(add_players(client, faker))

    res = client.get("/players")
    assert res.status_code == 200
    assert res.json() == created_players


def test_single(client, faker):
    created_players = list(add_players(client, faker))

    for p in created_players:
        res = client.get(f"/players/{p['id']}")
        assert res.status_code == 200
        assert res.json() == p


def test_single_non_existent(client, faker):
    res = client.get(f"/players/{87537345873}")
    assert res.status_code == 404
