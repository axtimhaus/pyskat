from faker import Faker
from fastapi.testclient import TestClient


def add_tables(client: TestClient, faker: Faker):
    for i in range(1, 5):
        remarks = faker.word()

        res = client.post("/tables", json={"remarks": remarks})
        assert res.status_code == 200
        yield res.json()


def test_all(client, faker):
    created_tables = list(add_tables(client, faker))

    res = client.get("/tables")
    assert res.status_code == 200
    assert res.json() == created_tables


def test_single(client, faker):
    created_tables = list(add_tables(client, faker))

    for p in created_tables:
        res = client.get(f"/tables/{p['id']}")
        assert res.status_code == 200
        assert res.json() == p


def test_single_non_existent(client, faker):
    res = client.get(f"/tables/{87537345873}")
    assert res.status_code == 404
