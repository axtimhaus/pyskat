def test_plain(client, faker):
    res = client.post("/tables", json={})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 0,
        "series_id": None,
        "remarks": "",
    }


def test_remarks(client, faker):
    remarks = faker.word()

    res = client.post("/tables", json={"remarks": remarks})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 0,
        "series_id": None,
        "remarks": remarks,
    }


def test_series_existing(client, faker):
    client.post("/series", json={"date": faker.date_time().isoformat()})
    res = client.post("/tables", json={"series_id": 1})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "size": 0,
        "series_id": 1,
        "remarks": "",
    }


def test_series_non_existing(client, faker):
    res = client.post("/tables", json={"series_id": 8798324})
    assert res.status_code == 404


def test_multiple(client, faker):
    for i in range(1, 5):
        remarks = faker.word()

        res = client.post("/tables", json={"remarks": remarks})
        assert res.status_code == 200
        assert res.json() == {
            "id": i,
            "size": 0,
            "series_id": None,
            "remarks": remarks,
        }
