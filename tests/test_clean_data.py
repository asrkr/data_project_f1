""""Testss de nettoyage et de la résolution de filiation des écuries."""

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
