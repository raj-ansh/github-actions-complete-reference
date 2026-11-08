"""Entry point for uvicorn: ``uvicorn shelfwise.main:app``."""

from shelfwise.app import create_app

app = create_app()
