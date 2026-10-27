"""Fixtures partagées par les tests."""

from pathlib import Path

import pytest

import config


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirige config.DB_PATH vers une base SQLite temporaire, détruite
    après le test."""
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path
