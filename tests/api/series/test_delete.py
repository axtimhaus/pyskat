from faker import Faker
from fastapi.testclient import TestClient


def add_series(client: TestClient, faker: Faker):
    name = faker.name()
    date = faker.date_time().isoformat()
    remarks = faker.word()

    res = client.post(
        "/series",
        json={
            "name": name,
            "date": date,
            "remarks": remarks,
        },
    )
    assert res.status_code == 200
    return res.json()


def test_delete(client, faker):
    created_series = add_series(client, faker)

    res = client.delete(f"/series/{created_series['id']}")
    assert res.status_code == 204
    assert client.get(f"/series/{created_series['id']}").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/series/{87537345873}")
    assert res.status_code == 404
