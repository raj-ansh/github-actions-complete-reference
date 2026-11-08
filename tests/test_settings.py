import pytest

from shelfwise.settings import load_settings


def test_missing_api_key_stops_start_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHELFWISE_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        load_settings()


def test_settings_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHELFWISE_API_KEY", "abc")
    monkeypatch.setenv("SHELFWISE_DB", "/data/books.db")
    settings = load_settings()
    assert settings.api_key == "abc"
    assert settings.database_path == "/data/books.db"
