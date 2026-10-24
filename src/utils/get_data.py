import json
import os
import time
import sqlite3
import pandas as pd
import requests
import config


def _get_json(url: str, params: dict | None = None, max_attempts: int = 5) -> dict:
    """Effectue une requête GET avec retries et gestion du HTTP 429."""
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


def _parse_races_to_df(all_races: list[dict]) -> pd.DataFrame:
    """Transforme la liste brute de courses (JSON) en DataFrame Pandas."""
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
                "driver_name": f"{drv.get('givenName', '')} {drv.get('familyName', '')}".strip(),
                "date_of_birth": drv.get("dateOfBirth"),
                "constructor_id": cons.get("constructorId"),
                "team_name": cons.get("name"),
                "position": res.get("position"),
                "grid": res.get("grid"),
                "status": res.get("status"),
                "points": res.get("points"),
            })
    return pd.DataFrame(rows)


def fetch_season_raw(year: int, force_download: bool = False) -> tuple[list[dict], pd.DataFrame]:
    """Récupère les résultats d'une saison : depuis le cache JSON local si disponible,
    sinon via l'API Jolpica."""
    os.makedirs(config.RAW_DIR, exist_ok=True)
    json_path = os.path.join(config.RAW_DIR, f"results_{year}.json")

    # 1. Utilisation du cache local JSON s'il existe
    if os.path.exists(json_path) and not force_download:
        with open(json_path, "r", encoding="utf-8") as f:
            all_races = json.load(f)
        return all_races, _parse_races_to_df(all_races)

    # 2. Requête API si le fichier n'existe pas
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

    # Sauvegarde du JSON brut
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_races, f, ensure_ascii=False, indent=2)

    return all_races, _parse_races_to_df(all_races)


def updat_raw_database(start_year: int = config.START_YEAR, end_year: int = config.END_YEAR, force_download: bool = False) -> None:
    """Remplit la table 'raw' de la db SQLite en lisant le cache JSON
    ou en téléchargeant les saisons manquantes."""
    all_dfs = []

    print(f"Construction de la table 'raw' ({start_year}-{end_year})...")

    for year in range(start_year, end_year + 1):
        try:
            _, df_year = fetch_season_raw(year, force_download=force_download)
            if df_year.empty:
                continue
            all_dfs.append(df_year)
            print(f"Saison {year} chargée.")
        except Exception as e:
            print(f"Erreur saison {year} : {e}")

    if all_dfs:
        full_df_raw = pd.concat(all_dfs, ignore_index=True)
        with sqlite3.connect(config.DB_PATH) as conn:
            full_df_raw.to_sql("raw", conn, if_exists="replace", index=False)
        print("Table 'raw' créée.")


if __name__ == "__main__":
    updat_raw_database()
