from faker import Faker
from fastapi.testclient import TestClient


def add_table(client: TestClient, faker: Faker):
    name = faker.name()
    active = faker.boolean()
    remarks = faker.word()

    res = client.post("/tables", json={"name": name, "active": active, "remarks": remarks})
    assert res.status_code == 200
    return res.json()


def test_delete(client, faker):
    created_table = add_table(client, faker)

    res = client.delete(f"/tables/{created_table['id']}")
    assert res.status_code == 204
    assert client.get(f"/tables/{created_table['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/tables/{87537345873}")
    assert res.status_code == 404
