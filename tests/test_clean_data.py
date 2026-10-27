""" "Tests de nettoyage et de la résolution de filiation des écuries."""

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from src.utils.clean_data import clean_raw_data, resolve_team

# Tests de resolve_team


def test_renamed_teams_share_one_key() -> None:
    """Minardi, Toro Rosso, AlphaTauri et RB sont la même écurie."""
    assert resolve_team("minardi", 2000) == "rb"
    assert resolve_team("toro_rosso", 2010) == "rb"
    assert resolve_team("alphatauri", 2022) == "rb"


def test_homonyms_are_split_by_era() -> None:
    """Alfa Romeo usine (1950) et Alfa Romeo - Sauber (2020) sont
    deux entités distinctes."""
    assert resolve_team("alfa", 1950) == "alfa_romeo_works"
    assert resolve_team("alfa", 2020) == "sauber"
    assert resolve_team("alfa", 1950) != resolve_team("alfa", 2020)


def test_chassis_engine_suffix_is_stripped() -> None:
    """Les identifiants châssis-moteur des années 60 remontent au constructeur."""
    assert resolve_team("lotus-climax", 1963) == "team_lotus"
    assert resolve_team("brabham-repco", 1966) == "brabham"


def test_unknown_id_is_kept_as_is() -> None:
    """Une écurie sans lignée connue garde son identifiant Ergast."""
    assert resolve_team("hesketh", 1975) == "hesketh"


def test_missing_id_returns_unknown() -> None:
    """Un identifiant absent ou vide est classé comme écurie inconnue."""
    assert resolve_team(None, 2000) == "unknown"
    assert resolve_team("", 2000) == "unknown"


# Test d'intégration de clean_raw_data (sur une base temporaire)


def _raw_row(**overrides: Any) -> dict[str, Any]:
    """Construit une ligne de la table raw (valeurs en chaînes, comme l'API).
    Les arguments nommés remplacent les valeurs par défaut, ce qui permet
    de créer des variantes en une ligne."""
    row: dict[str, Any] = {
        "season": "1963", "round": "2", "race_date": "1963-06-09", "circuit_id": "spa",
        "circuit_name": "Spa", "lat": "50.4372", "long": "5.9714", "country": "Belgium",
        "driver_id": "clark", "given_name": "Jim", "family_name": "Clark",
        "date_of_birth": "1936-03-04", "constructor_id": "lotus-climax",
        "team_name": "Lotus-Climax", "position": "1", "position_text": "1",
        "grid": "8", "status": "Finished", "points": "9",
    }
    row.update(overrides)
    return row


def test_clean_raw_data_builds_cleaned_table(tmp_db: Path) -> None:
    """La table cleaned est crée, enrichie et exclut l'Indy Car."""
    rows = [
        _raw_row(),
        _raw_row(season="1955", circuit_id="indianapolis", constructor_id="kurtis_kraft"),
        _raw_row(season="2023", constructor_id="alphatauri", date_of_birth=None),
    ]
    with sqlite3.connect(tmp_db) as conn:
        pd.DataFrame(rows).to_sql("raw", conn, index=False)

    clean_raw_data()

    with sqlite3.connect(tmp_db) as conn:
        cleaned = pd.read_sql_query("SELECT * FROM cleaned", conn)

    assert len(cleaned) == 2                        # La ligne d'Indy Car est exclue
    assert set(cleaned["team_key"]) == {"team_lotus", "rb"}
    assert cleaned["lat"].dtype.kind == "f"         # Typage
    assert cleaned.loc[0, "driver_name"] == "Jim Clark"
    assert cleaned.loc[0, "age_at_race"] == pytest.approx(27.26, abs=0.01)
    assert pd.isna(cleaned.loc[1, "age_at_race"])   # pas de date de naissance
