import pytest


@pytest.fixture
def add_players(client, faker):
    def yield_players():
        for i in range(1, 6):
            name = faker.name()
            res = client.post("/players", json={"name": name})
            assert res.status_code == 200
            yield res.json()
    return list(yield_players())

@pytest.fixture
def add_table(client, add_players):
    res = client.post("/tables", json={
        "player1_id": 1,
        "player2_id": 2,
        "player3_id": 3,
        "player4_id": 4,
    })
    assert res.status_code == 200
    return res.json()

@pytest.fixture
def add_tables(client, faker, add_players):
    def yield_tables():
        for i in range(1, 5):
            remarks = faker.word()
            res = client.post("/tables", json={
                "player1_id": 1,
                "player2_id": 2,
                "player3_id": 3,
                "player4_id": 4,
                "remarks": remarks,
            })
            assert res.status_code == 200
            yield res.json()
    return list(yield_tables())
