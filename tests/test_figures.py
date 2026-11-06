"""Tests des fonctions de la carte et de la fiche circuit (sans base ni Dash)."""

import pandas as pd
import pytest

from src.components.figures import (
    build_circuits_map,
    pole_win_rate,
    split_first_places,
)
from src.components.key_figures import figure_card
from src.utils.countries import country_fr


def _row(
    season: int, circuit_id: str, driver: str, position: int, grid: int
) -> dict[str, object]:
    """Une ligne de résultat (un pilote sur une course)."""
    circuits = {
        "monaco": ("Circuit de Monaco", "Monaco", 43.73, 7.42),
        "silverstone": ("Silverstone Circuit", "UK", 52.07, -1.02),
    }
    name, country, lat, long = circuits[circuit_id]
    return {
        "season": season,
        "round": 1,
        "circuit_id": circuit_id,
        "circuit_name": name,
        "country": country,
        "lat": lat,
        "long": long,
        "driver_name": driver,
        "position": position,
        "grid": grid,
    }


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


def test_map_one_point_per_circuit(df: pd.DataFrame) -> None:
    fig = build_circuits_map(df, 1950, 1953)
    assert len(fig.data[0].lat) == 2


def test_map_respects_period(df: pd.DataFrame) -> None:
    fig = build_circuits_map(df, 1950, 1950)
    assert len(fig.data[0].lat) == 1


def test_map_counts_races_and_translates_country(df: pd.DataFrame) -> None:
    fig = build_circuits_map(df, 1950, 1953)
    rows = {list(row)[0]: list(row) for row in fig.data[0].customdata}
    assert rows["monaco"][2] == 3
    assert rows["silverstone"][1] == "Royaume-Uni"


def test_split_first_places_wins(df: pd.DataFrame) -> None:
    regulars, once = split_first_places(df, "monaco", "position")
    assert list(regulars["driver_name"]) == ["Juan Fangio"]
    assert list(regulars["count"]) == [2]
    assert list(once["driver_name"]) == ["Alberto Ascari"]
    assert "1952" in str(once.iloc[0]["years"])


def test_split_first_places_poles(df: pd.DataFrame) -> None:
    regulars, once = split_first_places(df, "monaco", "grid")
    assert list(regulars["driver_name"]) == ["Alberto Ascari"]
    assert list(once["driver_name"]) == ["Juan Fangio"]


def test_split_first_places_unknown_circuit(df: pd.DataFrame) -> None:
    regulars, once = split_first_places(df, "spa", "position")
    assert regulars.empty
    assert once.empty


def test_pole_win_rate_circuit(df: pd.DataFrame) -> None:
    # 3 victoires à Monaco, 2 depuis la pole
    assert pole_win_rate(df, "monaco") == 66.7


def test_pole_win_rate_global(df: pd.DataFrame) -> None:
    assert pole_win_rate(df) == 50.0


def tet_pole_win_rate_no_race() -> None:
    assert pole_win_rate(pd.DataFrame(columns=["position", "grid"])) == 0.0


def test_country_fr() -> None:
    assert country_fr("UK") == "Royaume-Uni"
    assert country_fr("Monaco") == "Monaco"
    assert country_fr("Atlantide") == "Atlantide"


def test_figure_card_contains_label_and_value() -> None:
    card = str(figure_card("Grands Prix", 71))
    assert "Grands Prix" in card
    assert "71" in card
