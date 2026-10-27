"""Tests des fonctions utilitaires partagées."""

import sqlite3
from pathlib import Path

from src.utils.common_functions import table_exists


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
