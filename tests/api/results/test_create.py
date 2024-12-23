def test_existing(client, faker):
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
    assert res.json() == {"table_id": 1, "player_id": 2, "points": points, "won": won, "lost": lost, "remarks": ""}
