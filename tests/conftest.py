from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from shelfwise.app import create_app
from shelfwise.settings import Settings

API_KEY = "test-key"  # noqa: S105 - a fixture value, not a real secret
HEADERS = {"X-API-Key": API_KEY}
DUNE = {
    "isbn": "978-0-441-17271-9",
    "title": "Dune",
    "author": "Frank Herbert",
    "stock": 3,
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(database_path=str(tmp_path / "test.db"), api_key=API_KEY)
    with TestClient(create_app(settings)) as test_client:
        yield test_client
