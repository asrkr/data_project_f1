"""Récupération des résultats F1 (1950-2025) via l'API Jolpica/Ergast.

Les saisons sont mises en cache en JSON dans data/raw/, puis chargées
dans la table 'raw' de la base SQLite.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

import config


def _get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Effectue une requête GET avec retries et gestion du HTTP 429."""
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        try:
            r = requests.get(url, params=params, headers=config.HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"Erreur réseau ({e}), tentative {attempt}/{config.MAX_ATTEMPTS}")
            time.sleep(3 * attempt)
            continue

        if r.status_code == 200:
            result: dict[str, Any] = r.json()
            return result

        if r.status_code == 429:
            wait = min(15 * attempt, config.MAX_BACKOFF)
            print(f"Limite de requêtes de l'API atteinte, pause de {wait} s...")
            time.sleep(wait)
        else:
            print(f"HTTP {r.status_code}, tentative {attempt}/{config.MAX_ATTEMPTS}")
            time.sleep(3 * attempt)

    raise RuntimeError(f"Échec après {config.MAX_ATTEMPTS} tentatives : {url}")


def _flatten_result(race: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Aplatit un résultat de course (JSON imbriqué) en une ligne de table.
    Les valeurs sont gardées telles que renvoyées par l'API (chaînes),
    le typage se fera dans clean_data.
    """
    circuit = race.get("Circuit", {})
    location = circuit.get("Location", {})
    driver = result.get("Driver", {})
    constructor = result.get("Constructor", {})
    return {
        "season": race.get("season"),
        "round": race.get("round"),
        "race_date": race.get("date"),
        "circuit_id": circuit.get("circuitId"),
        "circuit_name": circuit.get("circuitName"),
        "lat": location.get("lat"),
        "long": location.get("long"),
        "country": location.get("country"),
        "driver_id": driver.get("driverId"),
        "given_name": driver.get("givenName"),
        "family_name": driver.get("familyName"),
        "date_of_birth": driver.get("dateOfBirth"),
        "constructor_id": constructor.get("constructorId"),
        "team_name": constructor.get("name"),
        "position": result.get("position"),
        "position_text": result.get("positionText"),    # Pour gérer les abandons
        "grid": result.get("grid"),
        "status": result.get("status"),
        "points": result.get("points"),
    }


def _parse_races_to_df(all_races: list[dict[str, Any]]) -> pd.DataFrame:
    """Transforme la liste brute de courses (JSON) en
    DataFrame Pandas : une ligne par résultat"""
    rows = [
        _flatten_result(race, result)
        for race in all_races
        for result in race.get("Results", [])
    ]
    return pd.DataFrame(rows)


def _cache_is_stale(json_path: Path, year: int) -> bool:
    """Indique si le cache d'une saison doit être re-téléchargé.
    Les saisons terminées sont figées, seule la saison la plus récente
    expire, après CACHE_MAX_AGE_DAYS jours (mécanisme de rafraîchissement).
    """
    if year < config.END_YEAR:
        return False
    age_days = (time.time() - json_path.stat().st_mtime) / 86400
    return age_days > config.CACHE_MAX_AGE_DAYS


def fetch_season_raw(
        year: int,
        force_download: bool = False
    ) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """Récupère les résultats d'une saison : depuis le cache JSON local si disponible
    et encore valide, sinon via l'API Jolpica."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    json_path = config.RAW_DIR / f"results_{year}.json"

    # 1. Utilisation du cache local JSON s'il existe e n'est pas encore périmé
    if json_path.exists() and not force_download and not _cache_is_stale(json_path, year):

        with json_path.open(encoding="utf-8") as f:
            cached_races: list[dict[str, Any]] = json.load(f)
        return cached_races, _parse_races_to_df(cached_races)

    # 2. Requête API si le fichier n'existe pas
    url = f"{config.API_BASE}/{year}/results.json"
    offset = 0
    races_dict: dict[int, dict[str, Any]] = {}

    while True:
        data = _get_json(url, params={"limit": config.PAGE_LIMIT, "offset": offset})["MRData"]
        races_list = data["RaceTable"]["Races"]

        # Une même course peut être coupée enntre eux pages : on fusionne ses résultats
        for race in races_list:
            rnd = int(race["round"])
            if rnd in races_dict:
                races_dict[rnd].setdefault("Results", []).extend(race.get("Results", []))
            else:
                race.setdefault("Results", [])
                races_dict[rnd] = race

        offset += config.PAGE_LIMIT
        if offset >= int(data["total"]):
            break
        time.sleep(config.PAUSE)

    all_races = [races_dict[r] for r in sorted(races_dict.keys())]

    # Sauvegarde du JSON brut
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(all_races, f, ensure_ascii=False, indent=2)

    return all_races, _parse_races_to_df(all_races)


def update_raw_database(
        start_year: int = config.START_YEAR,
        end_year: int = config.END_YEAR,
        force_download: bool = False
    ) -> None:
    """Remplit la table 'raw' de la db SQLite en lisant le cache JSON
    ou en téléchargeant les saisons manquantes."""
    all_dfs = []

    print(f"Construction de la table 'raw' ({start_year}-{end_year})...")

    for year in range(start_year, end_year + 1):
        try:
            _, df_year = fetch_season_raw(year, force_download=force_download)
        except (RuntimeError, requests.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"Erreur saison {year} : {e}")
            continue
        if not df_year.empty:
            all_dfs.append(df_year)
            print(f"Saison {year} chargée.")

    if all_dfs:
        full_df_raw = pd.concat(all_dfs, ignore_index=True)
        with sqlite3.connect(config.DB_PATH) as conn:
            full_df_raw.to_sql("raw", conn, if_exists="replace", index=False)
        print("Table 'raw' créée.")


if __name__ == "__main__":
    update_raw_database()
