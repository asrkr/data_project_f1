"""Tests des fonctions utilitaires partagées."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import pytest

import config
from src.utils.common_functions import load_cleaned, table_exists


def test_table_exists_false_when_db_missing(tmp_db: Path) -> None:
    """Sans fichier de base, acune table n'existe (et rien ne plante)."""
    assert not tmp_db.exists()
    assert table_exists("cleaned") is False


def test_table_exists_detects_created_table(tmp_db: Path) -> None:
    """Une table créée est détectée, une table absente ne l'est pas."""
    with sqlite3.connect(tmp_db) as conn:
        conn.execute("CREATE TABLE cleaned (id INTEGER)")

    assert table_exists("cleaned") is True
    assert table_exists("raw") is False


@pytest.mark.usefixtures("tmp_db")
def test_load_cleaned_returns_table() -> None:
    """La table 'cleaned' est relue à l'identique."""
    expected = pd.DataFrame({"season": [2024, 2025], "driver_name": ["A", "B"]})
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        expected.to_sql("cleaned", conn, index=False)

    result = load_cleaned()

    assert list(result.columns) == ["season", "driver_name"]
    assert len(result) == 2


@pytest.mark.usefixtures("tmp_db")
def test_load_cleaned_missing_table() -> None:
    """Une erreur explicite est levée si la table est absente."""
    with pytest.raises(RuntimeError, match="cleaned"):
        load_cleaned()
