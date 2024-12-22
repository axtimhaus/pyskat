import pytest
from faker import Faker
from fastapi.testclient import TestClient

import pyskat


@pytest.fixture
def settings(tmp_path):
    return pyskat.Settings(
        database_url=f"sqlite:///{tmp_path}/test.db",
    )


@pytest.fixture
def client(settings) -> TestClient:
    return TestClient(pyskat.api.create_app(settings))


@pytest.fixture
def faker():
    return Faker()
