import time
import sqlite3
import pandas as pd
import requests
import config


def fetch_raw_data(year: int = 2024) -> pd.DataFrame:
    """On récupère l'intégralité des résultats bruts d'une saison via Jolpica.
    Gestion de la pagination ajoutée."""
    url = f"{config.API_BASE}/{year}/results.json"
    offset = 0
    rows = []

    while True:
        response = requests.get(
            url,
            params={"limit": config.PAGE_LIMIT, "offset": offset},
            headers=config.HEADERS,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()["MRData"]

        races = data["RaceTable"]["Races"]
        for race in races:
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
                    "lat": float(loc.get("lat", 0)),
                    "long": float(loc.get("long", 0)),
                    "country": loc.get("country"),
                    "driver_id": drv.get("driverId"),
                    "driver_name": f"{drv.get('givenName', '')} {drv.get('familyName', '')}".strip(),
                    "date_of_birth": drv.get("dateOfBirth"),
                    "constructor_id": cons.get("constructorId"),
                    "team_name": cons.get("name"),
                    "position": res.get("position"),
                    "status": res.get("status"),
                })

        offset += config.PAGE_LIMIT
        if offset >= int(data["total"]):
            break
        time.sleep(config.PAUSE)

    return pd.DataFrame(rows)


def save_raw_to_sqlite() -> None:
    """Sauvegarde les données brutes dans la table raw de SQLite."""
    df_raw = fetch_raw_data(2024)
    with sqlite3.connect(config.DB_PATH) as conn:
        df_raw.to_sql("raw", conn, if_exists="replace", index=False)
    print("Table 'raw' créée avec succès dans SQLite.")


if __name__ == "__main__":
    save_raw_to_sqlite()
