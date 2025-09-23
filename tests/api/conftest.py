import pytest
from faker import Faker
from fastapi.testclient import TestClient

import pyskat.dependencies
import pyskat.api


@pytest.fixture
def settings(tmp_path) -> pyskat.dependencies.Settings:
    return pyskat.dependencies.Settings(
        database_url=f"sqlite:///{tmp_path}/test.db",
    )


@pytest.fixture
def client(settings, monkeypatch) -> TestClient:
    monkeypatch.setitem(
        pyskat.api.app.dependency_overrides,
        pyskat.dependencies.get_settings,
        lambda: settings,
    )
    client = TestClient(pyskat.api.app)
    return client


@pytest.fixture
def faker():
    return Faker()
