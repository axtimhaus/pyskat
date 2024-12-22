from faker import Faker
from fastapi.testclient import TestClient


def add_player(client: TestClient, faker: Faker):
    name = faker.name()
    active = faker.boolean()
    remarks = faker.word()

    res = client.post("/players", json={"name": name, "active": active, "remarks": remarks})
    assert res.status_code == 200
    return res.json()


def test_delete(client, faker):
    created_player = add_player(client, faker)

    res = client.delete(f"/players/{created_player['id']}")
    assert res.status_code == 204
    assert client.get(f"/players/{created_player['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/players/{87537345873}")
    assert res.status_code == 404
