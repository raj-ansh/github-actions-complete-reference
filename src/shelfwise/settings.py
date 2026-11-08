"""Configuration, read from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str
    api_key: str


def load_settings() -> Settings:
    """Build settings from the environment.

    ``SHELFWISE_API_KEY`` has no default: a deployment that forgets it must
    fail at start-up rather than run with a guessable key.
    """
    api_key = os.environ.get("SHELFWISE_API_KEY", "")
    if not api_key:
        raise RuntimeError("SHELFWISE_API_KEY must be set")
    return Settings(
        database_path=os.environ.get("SHELFWISE_DB", "shelfwise.db"),
        api_key=api_key,
    )
