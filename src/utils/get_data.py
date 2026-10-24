import json
import os
import time
import sqlite3
import pandas as pd
import requests
import config


def _get_json(url: str, params: dict | None = None, max_attempts: int = 5) -> dict:
    """Effectue une requête GET avec retries et gestion explicite du HTTP 429/"""
    for attempt in range(1, max_attempts + 1):
        try:
            r = requests.get(url, params=params, headers=config.HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"Erreur réseau ({e}), tentative {attempt}/{max_attempts}")
            time.sleep(3 * attempt)
            continue

        if r.status_code == 200:
            return r.json()

        if r.status_code == 429:
            wait = 15 * attempt
            print(f"Limite de requêtes de l'API atteinte, pause de {wait} s...")
            time.sleep(wait)
        else:
            print(f"HTTP {r.status_code}, tentative {attempt}/{max_attempts}")
            time.sleep(3 * attempt)

    raise RuntimeError(f"Échec après {max_attempts} tentatives : {url}")


def fetch_season_raw(year: int) -> tuple[list[dict], pd.DataFrame]:
    """Récupère les résultats bruts d'une saison via Jolpica en gérant la pagination et les limites."""
    url = f"{config.API_BASE}/{year}/results.json"
    offset = 0
    races_dict = {}

    while True:
        data = _get_json(url, params={"limit": config.PAGE_LIMIT, "offset": offset})["MRData"]
        races_list = data["RaceTable"]["Races"]

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

    rows = []
    for race in all_races:
        circuit = race.get("Circuit", {})
        loc = circuit.get("Location", {})
        for res in race.get("Results", []):
            drv = res.get("Driver", {})
            cons = res.get("Constructor", {})
            rows.append({
                "season": int(race["season"]),
                "round": int(race["round"]),
                "race_date": race.get("date"),
                "circuit_id": circuit.get("circuitId"),
                "circuit_name": circuit.get("circuitName"),
                "lat": float(loc.get("lat")) if loc.get("lat") else None,
                "long": float(loc.get("long")) if loc.get("long") else None,
                "country": loc.get("country"),
                "driver_id": drv.get("driverId"),
                "driverName": f"{drv.get('givenName', '')} {drv.get('familyName', '')}".strip(),
                "date_of_birth": drv.get("dateOfBirth"),
                "constructor_id": cons.get("constructorId"),
                "team_name": cons.get("name"),
                "position": res.get("position"),
                "grid": res.get("grid"),
                "status": res.get("status"),
                "points": res.get("points"),
            })

    return all_races, pd.DataFrame(rows)


def updat_raw_database(start_year: int = config.START_YEAR, end_year: int = config.END_YEAR) -> None:
    """Parcourt l'ensemble des saisons, sauvegarde les fichiers JSON et remplit la table raw."""
    os.makedirs(config.RAW_DIR, exist_ok=True)
    all_dfs = []

    for year in range(start_year, end_year + 1):
        try:
            raw_races, df_year = fetch_season_raw(year)
            if df_year.empty:
                continue

            json_path = os.path.join(config.RAW_DIR, f"results_{year}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(raw_races, f, ensure_ascii=False, indent=2)

            all_dfs.append(df_year)
            print(f"Saison {year} enregistrée.")

        except Exception as e:
            print(f"Erreur saison {year} : {e}")

    if all_dfs:
        full_raw_df = pd.concat(all_dfs, ignore_index=True)
        with sqlite3.connect(config.DB_PATH) as conn:
            full_raw_df.to_sql("raw", conn, if_exists="replace", index=False)
        print("Extraction terminée et table 'raw' mise à jour.")


if __name__ == "__main__":
    updat_raw_database()
