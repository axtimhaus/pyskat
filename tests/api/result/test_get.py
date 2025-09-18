from faker import Faker
from fastapi.testclient import TestClient


def add_results(client: TestClient, faker: Faker):
    for i in range(1, 5):
        for j in range(1, 2):
            score = faker.random_int(0, 1000)
            won = faker.random_int(0, 10)
            lost = faker.random_int(0, 10)

            res = client.post(
                f"/result/{j}/{i}",
                json={
                    "score": score,
                    "won": won,
                    "lost": lost,
                },
            )
            assert res.status_code == 200
            yield res.json()


def test_all(client, faker):
    created_results = list(add_results(client, faker))

    res = client.get("/result")
    assert res.status_code == 200
    assert res.json() == created_results


def test_single(client, faker):
    created_results = list(add_results(client, faker))

    for r in created_results:
        res = client.get(f"/result/{r['match_id']}/{r['player_id']}")
        assert res.status_code == 200
        res_json = res.json()
        del res_json["player"]
        del res_json["match"]
        assert res_json == r


def test_single_non_existent(client, faker):
    res = client.get(f"/result/6545/537345873")
    assert res.status_code == 404
