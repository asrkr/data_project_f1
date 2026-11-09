"""Fixtures partagées par les tests."""

from pathlib import Path

import pandas as pd
import pytest

import config
from src.app import create_app

# Les pages appellent dash.register_page à l'import : il faut une app instanciée
create_app()


def _row(
    season: int, circuit_id: str, driver: str, position: int, grid: int
) -> dict[str, object]:
    """Une ligne de résultat (un pilote sur une course)."""
    circuits = {
        "monaco": ("Circuit de Monaco", "Monaco", 43.73, 7.42),
        "silverstone": ("Silverstone Circuit", "UK", 52.07, -1.02),
    }
    name, country, lat, long = circuits[circuit_id]
    team_key, team_name = (
        ("alfa", "Alfa Romeo") if driver == "Juan Fangio" else ("ferrari", "Ferrari")
    )
    return {
        "season": season,
        "round": 1,
        "circuit_id": circuit_id,
        "circuit_name": name,
        "country": country,
        "lat": lat,
        "long": long,
        "driver_name": driver,
        "team_key": team_key,
        "team_name": team_name,
        "position": position,
        "grid": grid,
    }


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirige config.DB_PATH vers une base SQLite temporaire, détruite
    après le test."""
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return db_path


@pytest.fixture
def df() -> pd.DataFrame:
    """4 courses : Fangio gagne 3 fois (2 à Monaco), Ascari 1 fois (Monaco)."""
    return pd.DataFrame(
        [
            _row(1950, "monaco", "Juan Fangio", 1, 1),
            _row(1950, "monaco", "Alberto Ascari", 2, 2),
            _row(1951, "silverstone", "Juan Fangio", 1, 3),
            _row(1951, "silverstone", "Alberto Ascari", 2, 1),
            _row(1952, "monaco", "Alberto Ascari", 1, 1),
            _row(1952, "monaco", "Juan Fangio", 2, 2),
            _row(1953, "monaco", "Juan Fangio", 1, 2),
            _row(1953, "monaco", "Alberto Ascari", 2, 1),
        ]
    )


@pytest.fixture
def ages() -> pd.DataFrame:
    """3 participants, 2 dans les années 50, 2 victoires."""
    return pd.DataFrame(
        {
            "season": [1950, 1951, 1965],
            "position": [1, 2, 1],
            "age_at_race": [25.0, 30.5, 40.0]
        }
    )
