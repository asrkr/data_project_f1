"""Tests de la récupération des données (sans appel réseau)."""

# Les fonctions privées (_flatten_results, ...) sont testées volontairement.

from typing import Any

from src.utils import get_data

# Fausse course au format de l'API : deux résultats dont un abandon.
FAKE_RACE: dict[str, Any] = {
    "season": "1999",
    "round": "1",
    "date": "1999-03-07",
    "Circuit": {
        "circuitId": "albert_park",
        "circuitName": "Albert Park",
        "Location": {
            "lat": "-37.8497",
            "long": "144.968",
            "country": "Australia",
        },
    },
    "Results": [
        {
            "position": "1", "positionText": "1", "grid": "3", "points": "10",
            "status": "Finished",
            "Driver": {
                "driverId": "irvine", "givenName": "Eddie", "familyName": "Irvine", "dateOfBirth": "1965-11-10",
            },
            "Constructor": {
                "constructorId": "ferrari", "name": "Ferrari",
            },
        },
        {
            "position": "2", "positionText": "R", "grid": "1", "points": "0",
            "status": "Accident",
            "Driver": {
                "driverId": "hakkinen", "givenName": "Mika", "familyName": "Häkkinen", "datOfBirth": "1968-09-28",
            },
            "Constructor": {
                "constructorId": "mclaren", "name": "McLaren",
            },
        },
    ],
}


def test_flatten_result_reads_nested_key() -> None:
    """Les champs imbriqués (Circuit.Location, Driver, Constructor) sont aplatis."""
    row = get_data._flatten_result(FAKE_RACE, FAKE_RACE["Results"][0])
    assert row["lat"] == "-37.8497"
    assert row["country"] == "Australia"
    assert row["driver_id"] == "irvine"
    assert row["constructor_id"] == "ferrari"


def test_parse_races_to_df_one_row_per_result() -> None:
    """Chaque résultat de pilote devient une ligne, abandons compris."""
    df = get_data._parse_races_to_df([FAKE_RACE, FAKE_RACE])
    assert len(df) == 4     # 2 courses * 2 résultats
    assert list(df["position_text"]) == ["1", "R", "1", "R"]
