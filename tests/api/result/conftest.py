from sqlalchemy.testing import fixture


@fixture(autouse=True)
def add_base_data(client, faker):
    for i in range(1, 8):
        assert client.post("/player", json={"name": faker.name()}).status_code == 200

    assert client.post("/match", json={}).status_code == 200
    assert client.post("/match", json={}).status_code == 200
