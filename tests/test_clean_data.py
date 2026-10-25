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
