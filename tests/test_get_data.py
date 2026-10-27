"""Tests de la récupération des données (sans appel réseau)."""

import json
import os
import time
from pathlib import Path
from typing import Any, NoReturn

import pytest

import config
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
                "driverId": "irvine", "givenName": "Eddie", "familyName": "Irvine",
                "dateOfBirth": "1965-11-10",
            },
            "Constructor": {
                "constructorId": "ferrari", "name": "Ferrari",
            },
        },
        {
            "position": "2", "positionText": "R", "grid": "1", "points": "0",
            "status": "Accident",
            "Driver": {
                "driverId": "hakkinen", "givenName": "Mika", "familyName": "Häkkinen",
                "datOfBirth": "1968-09-28",
            },
            "Constructor": {
                "constructorId": "mclaren", "name": "McLaren",
            },
        },
    ],
}

# Les fonctions privées (_flatten_results, ...) sont testées volontairement.


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


def test_cache_is_stale_only_for_latest_season(tmp_path: Path) -> None:
    """Seule la saison END_YEAR expire. Une saison terminée reste
    valide même si elle est ancienne."""
    cache = tmp_path / "results.json"
    cache.write_text("[]", encoding="utf-8")
    # On vieillit artificiellement le fichier au-delà de la durée de validité
    old_timestamp = time.time() - (config.CACHE_MAX_AGE_DAYS + 1) * 86400
    os.utime(cache, (old_timestamp, old_timestamp))

    assert get_data._cache_is_stale(cache, config.END_YEAR - 1) is False
    assert get_data._cache_is_stale(cache, config.END_YEAR) is True


def test_fetch_season_raw_uses_cache_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
)-> None:
    """Si le JSON est en cache, aucune requête HTTP ne doit partir."""
    monkeypatch.setattr(config, "RAW_DIR", tmp_path)
    cache_file = tmp_path / "results_1999.json"
    cache_file.write_text(json.dumps([FAKE_RACE]), encoding="utf-8")

    def _no_network(*_args: Any, **_kwargs: Any) -> NoReturn:
        raise AssertionError("appel réseau inattendu")

    # Toute tentative d'appel à l'API fera échouer le test
    monkeypatch.setattr(get_data.requests, "get", _no_network)

    races, df = get_data.fetch_season_raw(1999)
    assert len(races) == 1
    assert len(df) == 2
