"""Tests des fonctions de la carte et de la fiche circuit (sans base ni Dash)."""

import pandas as pd

from src.components.figures import (
    _years,
    build_age_histogram,
    build_circuit_top,
    build_circuits_map,
    build_team_wins,
    pole_win_rate,
    split_first_places,
)
from src.components.key_figures import figure_card
from src.utils.countries import country_fr


def test_map_one_point_per_circuit(df: pd.DataFrame) -> None:
    """n seul point par circuit, même avec plusieurs courses."""
    fig = build_circuits_map(df, 1950, 1953)
    assert len(fig.data[0].lat) == 2


def test_map_respects_period(df: pd.DataFrame) -> None:
    """Seuls les circuits de la période sont affichés."""
    fig = build_circuits_map(df, 1950, 1950)
    assert len(fig.data[0].lat) == 1


def test_map_counts_races_and_translates_country(df: pd.DataFrame) -> None:
    """Le nombre de courses et le pays traduit sont dans customdata."""
    fig = build_circuits_map(df, 1950, 1953)
    rows = {list(row)[0]: list(row) for row in fig.data[0].customdata}
    assert rows["monaco"][2] == 3
    assert rows["silverstone"][1] == "Royaume-Uni"


def test_split_first_places_wins(df: pd.DataFrame) -> None:
    """Vainqueurs multiples d'un côté, vainqueurs uniques de l'autre."""
    regulars, once = split_first_places(df, "monaco", "position")
    assert list(regulars["driver_name"]) == ["Juan Fangio"]
    assert list(regulars["count"]) == [2]
    assert list(once["driver_name"]) == ["Alberto Ascari"]
    assert "1952" in str(once.iloc[0]["years"])


def test_split_first_places_poles(df: pd.DataFrame) -> None:
    """Même découpage pour les départs en 1re position."""
    regulars, once = split_first_places(df, "monaco", "grid")
    assert list(regulars["driver_name"]) == ["Alberto Ascari"]
    assert list(once["driver_name"]) == ["Juan Fangio"]


def test_split_first_places_unknown_circuit(df: pd.DataFrame) -> None:
    """Circuit inconnu : deux tableaux vides."""
    regulars, once = split_first_places(df, "spa", "position")
    assert regulars.empty
    assert once.empty


def test_pole_win_rate_circuit(df: pd.DataFrame) -> None:
    """Taux pole → victoire d'un circuit."""
    # 3 victoires à Monaco, 2 depuis la pole
    assert pole_win_rate(df, "monaco") == 66.7


def test_pole_win_rate_global(df: pd.DataFrame) -> None:
    """Taux pole → victoire sur tous les circuits."""
    assert pole_win_rate(df) == 50.0


def tet_pole_win_rate_no_race() -> None:
    """Sans victoire, le taux vaut 0."""
    assert pole_win_rate(pd.DataFrame(columns=["position", "grid"])) == 0.0


def test_country_fr() -> None:
    """Traduction connue, pays inchangé, pays inconnu."""
    assert country_fr("UK") == "Royaume-Uni"
    assert country_fr("Monaco") == "Monaco"
    assert country_fr("Atlantide") == "Atlantide"


def test_figure_card_contains_label_and_value() -> None:
    """La vignette contient le libellé et la valeur."""
    card = str(figure_card("Grands Prix", 71))
    assert "Grands Prix" in card
    assert "71" in card


def test_years_sorted() -> None:
    """Les saisons sont triées et séparées par des virgules."""
    assert _years(pd.Series([1957, 1954, 1955])) == "1954, 1955, 1957"


def test_age_histogram_overlay_decade_on_history(ages: pd.DataFrame) -> None:
    """Trace grise = toute l'histoire, trace rouge = la décennie."""
    fig = build_age_histogram(ages, 1950)
    assert len(fig.data) == 2
    assert list(fig.data[0].x) == [25.0, 30.5, 40.0]
    assert list(fig.data[1].x) == [25.0, 30.5]
    assert fig.data[1].name == "Années 1950"


def test_age_histogram_winners_only(ages: pd.DataFrame) -> None:
    """Avec winners_only, seules les victoires sont comptées."""
    fig = build_age_histogram(ages, 1960, winners_only=True)
    assert list(fig.data[0].x) == [25.0, 40.0]
    assert list(fig.data[1].x) == [40.0]


def test_age_histogram_has_title(ages: pd.DataFrame) -> None:
    """La figure porte un titre mentionnant la décennie."""
    fig = build_age_histogram(ages, 1950, False)
    assert "1950" in fig.layout.title.text


def test_circuit_top_height_and_label(df: pd.DataFrame) -> None:
    """Hauteur proportionnelle au nombre de pilotes, axe nommé."""
    regulars, _ = split_first_places(df, "monaco", "position")
    fig = build_circuit_top(regulars, "Victoires")
    assert fig.layout.height == 80 + 30 * len(regulars)
    assert fig.layout.xaxis.title.text == "Victoires"


def test_build_team_wins_counts_by_team_key(df: pd.DataFrame) -> None:
    """Le graphique compte une victoire par Grand Prix, regroupée par team_key."""
    fig = build_team_wins(df)
    assert "Top 10" in fig.layout.title.text
    assert fig.layout.xaxis.title.text == "Victoires"
    assert fig.layout.yaxis.title.text == "Écurie"
    assert fig.data[0].x.sum() == int((df["position"] ==1).sum())


def test_build_team_wins_respects_top(df: pd.DataFrame) -> None:
    """Le paramètre top limite le nombre de barres."""
    fig = build_team_wins(df, top=1)
    assert len(fig.data[0].y) == 1
