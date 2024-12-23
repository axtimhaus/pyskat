from faker import Faker
from fastapi.testclient import TestClient


def add_results(client: TestClient, faker: Faker):
    for i in range(1, 5):
        for j in range(1, 2):
            points = faker.random_int(0, 1000)
            won = faker.random_int(0, 10)
            lost = faker.random_int(0, 10)

            res = client.post(
                f"/results/{j}/{i}",
                json={
                    "points": points,
                    "won": won,
                    "lost": lost,
                },
            )
            assert res.status_code == 200
            yield res.json()


def test_all(client, faker):
    created_results = list(add_results(client, faker))

    res = client.get("/results")
    assert res.status_code == 200
    assert res.json() == created_results


def test_single(client, faker):
    created_results = list(add_results(client, faker))

    for r in created_results:
        res = client.get(f"/results/{r['table_id']}/{r['player_id']}")
        assert res.status_code == 200
        assert res.json() == r


def test_single_non_existent(client, faker):
    res = client.get(f"/results/6545/537345873")
    assert res.status_code == 404
