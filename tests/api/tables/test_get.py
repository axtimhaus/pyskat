from faker import Faker
from fastapi.testclient import TestClient


def test_all(client, faker, add_tables):
    res = client.get("/tables")
    assert res.status_code == 200
    assert res.json() == add_tables


def test_single(client, faker, add_tables):
    for p in add_tables:
        res = client.get(f"/tables/{p['id']}")
        assert res.status_code == 200
        assert res.json() == p


def test_single_non_existent(client, faker, add_tables):
    res = client.get(f"/tables/{87537345873}")
    assert res.status_code == 404
