from faker import Faker
from fastapi.testclient import TestClient


def add_result(client: TestClient, faker: Faker):
    points = faker.random_int(0, 1000)
    won = faker.random_int(0, 10)
    lost = faker.random_int(0, 10)

    res = client.post(
        "/results/1/2",
        json={
            "points": points,
            "won": won,
            "lost": lost,
        },
    )
    assert res.status_code == 200
    return res.json()


def test_delete(client, faker):
    add_result(client, faker)
    res = client.delete("/results/1/2")
    assert res.status_code == 204
    assert client.get("/results/1/2").status_code == 404


def test_delete_non_existent(client, faker):
    res = client.delete(f"/results/87537/345873")
    assert res.status_code == 404
