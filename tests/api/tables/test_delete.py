from faker import Faker
from fastapi.testclient import TestClient
from rich.pretty import pprint


def test_delete(client, faker, add_table):

    res = client.delete(f"/tables/{add_table['id']}")
    assert res.status_code == 204
    assert client.get(f"/tables/{add_table['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/tables/{87537345873}")
    assert res.status_code == 404
