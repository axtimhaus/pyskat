import pytest


@pytest.fixture
def add_players(client, faker):
    def yield_players():
        for i in range(1, 6):
            name = faker.name()
            res = client.post("/player", json={"name": name})
            assert res.status_code == 200
            yield res.json()

    return list(yield_players())


@pytest.fixture
def add_match(client, add_players, faker):
    remarks = faker.word()
    res = client.post(
        "/match",
        json={"player_ids": [1, 2, 3, 4], "remarks": remarks},
    )
    assert res.status_code == 200
    return res.json()


@pytest.fixture
def add_matches(client, faker, add_players):
    def yield_matches():
        for i in range(1, 5):
            remarks = faker.word()
            res = client.post(
                "/match",
                json={
                    "player_ids": [1, 2, 3, 4],
                    "remarks": remarks,
                },
            )
            assert res.status_code == 200
            yield res.json()

    return list(yield_matches())
