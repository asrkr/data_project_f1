"""Fonctions utilitaires partagées par le pipeline et le dashboard."""

import sqlite3
from contextlib import closing

import pandas as pd

import config


def table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base SQLite
    (False si la table est absente).
    
    C'est ce test, et non la présence du cache JSON qui décide si
    on lance le pipeline. Après un clone du projet, seule la base
    SQLite est présente et c'est suffisant."""
    if not config.DB_PATH.exists():
        return False
    # sqlite_master est la table système de SQLite quii liste toutes les tables
    query = "SELECT name FROM sqlite_master WHERE type='table' and name=?"
    with sqlite3.connect(config.DB_PATH) as conn:
        return conn.execute(query, (table_name,)).fetchone() is not None


def load_cleaned() -> pd.DataFrame:
    """Charge la table 'cleaned' de la base SQLite dans un DataFrame.
    Lève une RuntimeError si la table 'cleaned' n'existe pas encore."""
    if not table_exists("cleaned"):
        raise RuntimeError(
            "Table 'cleaned' absente : lancez 'uv run python -m src.utils.get_data' "
            "puis 'uv run python- m src.utils.clean_data'."
        )
    with closing(sqlite3.connect(config.DB_PATH)) as conn:
        return pd.read_sql("SELECT * FROM cleaned", conn)
