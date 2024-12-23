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


def test_name(client, faker):
    created_series = add_series(client, faker)
    new_name = faker.name()

    res = client.patch(f"/series/{created_series['id']}", json={"name": new_name})
    assert res.status_code == 200
    assert res.json() == created_series | {"name": new_name}


def test_date(client, faker):
    created_series = add_series(client, faker)
    new_date = faker.date_time().isoformat()

    res = client.patch(f"/series/{created_series['id']}", json={"date": new_date})
    assert res.status_code == 200
    assert res.json() == created_series | {"date": new_date}


def test_remarks(client, faker):
    created_series = add_series(client, faker)
    new_remarks = faker.word()

    res = client.patch(f"/series/{created_series['id']}", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == created_series | {"remarks": new_remarks}


def test_name_date_remarks(client, faker):
    created_series = add_series(client, faker)
    new_name = faker.name()
    new_date = faker.date_time().isoformat()
    new_remarks = faker.word()

    res = client.patch(
        f"/series/{created_series['id']}",
        json={
            "name": new_name,
            "date": new_date,
            "remarks": new_remarks,
        },
    )
    assert res.status_code == 200
    assert res.json() == created_series | {
        "name": new_name,
        "date": new_date,
        "remarks": new_remarks,
    }


def test_non_existent(client, faker):
    res = client.patch(f"/series/{984379843}", json={})
    assert res.status_code == 404
