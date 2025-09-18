from faker import Faker
from fastapi.testclient import TestClient


def add_result(client: TestClient, faker: Faker):
    score = faker.random_int(0, 1000)
    won = faker.random_int(0, 10)
    lost = faker.random_int(0, 10)

    res = client.post(
        "/result/1/2",
        json={
            "score": score,
            "won": won,
            "lost": lost,
        },
    )
    assert res.status_code == 200
    return res.json()


def test_score(client, faker):
    created_result = add_result(client, faker)
    new_score = faker.random_int(0, 1000)

    res = client.patch("/result/1/2", json={"score": new_score})
    assert res.status_code == 200
    assert res.json() == created_result | {"score": new_score}


def test_won(client, faker):
    created_result = add_result(client, faker)
    new_won = faker.random_int(0, 10)

    res = client.patch(f"/result/1/2", json={"won": new_won})
    assert res.status_code == 200
    assert res.json() == created_result | {"won": new_won}


def test_lost(client, faker):
    created_result = add_result(client, faker)
    new_lost = faker.random_int(0, 10)

    res = client.patch(f"/result/1/2", json={"lost": new_lost})
    assert res.status_code == 200
    assert res.json() == created_result | {"lost": new_lost}


def test_remarks(client, faker):
    created_result = add_result(client, faker)
    new_remarks = faker.word()

    res = client.patch(f"/result/1/2", json={"remarks": new_remarks})
    assert res.status_code == 200
    assert res.json() == created_result | {"remarks": new_remarks}


def test_non_existent(client, faker):
    res = client.patch(f"/result/984379843/4242", json={})
    assert res.status_code == 404
