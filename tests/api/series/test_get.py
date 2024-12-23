from faker import Faker
from fastapi.testclient import TestClient


def add_series(client: TestClient, faker: Faker):
    for i in range(1, 5):
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
        yield {
            "id": i,
            "name": name,
            "date": date,
            "remarks": remarks,
        }


def test_all(client, faker):
    created_series = list(add_series(client, faker))

    res = client.get("/series")
    assert res.status_code == 200
    assert res.json() == created_series


def test_single(client, faker):
    created_series = list(add_series(client, faker))

    for p in created_series:
        res = client.get(f"/series/{p['id']}")
        assert res.status_code == 200
        assert res.json() == p


def test_single_non_existent(client, faker):
    res = client.get(f"/series/{87537345873}")
    assert res.status_code == 404
