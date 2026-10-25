import re
import sqlite3
import pandas as pd
import config


# 1) Lignées simples : constructorId -> clé canonique
TEAM_LINEAGE = {
    # Usine d'Enstone (Alpine)
    "toleman": "alpine",
    "benetton": "alpine",
    "lotus_f1": "alpine",
    "alpine": "alpine",
    # Usine de Silverstone (Aston Martin)
    "jordan": "aston_martin",
    "mf1": "aston_martin",
    "spyker_mf1": "aston_martin",
    "spyker": "aston_martin",
    "force_india": "aston_martin",
    "racing_point": "aston_martin",
    # Usine de Brackley (Mercedes)
    "tyrrell": "mercedes",
    "bar": "mercedes",
    "brawn": "mercedes",
    # Usine de Milton Keynes (Red Bull)
    "stewart": "red_bull",
    "jaguar": "red_bull",
    "red_bull": "red_bull",
    # Usine de Faenza (RB / Racing Bulls)
    "minard": "rb",
    "toro_rosso": "rb",
    "alphatauri": "rb",
    "rb": "rb",
    # Usine de Hinwil (Sauber)
    "sauber": "sauber",
    "bmw_sauber": "sauber",
    # Ecuries stables
    "ferrari": "ferrari",
    "mclaren": "mclaren",
    "haas": "haas",
    "williams": "williams",
    # Equipes disparues
    "lotus_racing": "caterham",
    "caterham": "caterham",
    "virgin": "manor",
    "marussia": "manor",
    "ligier": "prost",
    "prost": "prost",
    "arrows": "arrows",
    "footwork": "arrows",
    "march": "march",
    "leyton_house": "march",
    "osella": "fondmetal",
    "fondmetal": "fondmetal",
    "coloni": "andrea_moda",
    "onyx": "monteverdi",
    "monteverdi": "monteverdi",
    "ensign": "theodore",
    "theodore": "theodore",
    "dallara": "scuderia_italia",
    "larrousse": "larrousse",
    "wolf_williams": "wolf",
    "wolf": "wolf",
    "team_lotus": "team_lotus",
}

# 2) HOMONYMES PAR EPOQUE : résolution par (id, année_debut, année_fin, clé)
LINEAGE_BY_YEAR = [
    ("renault", 1977, 1985, "renault_works_80s"),
    ("renault", 2002, 2011, "alpine"),
    ("renault", 2016, 2020, "alpine"),
    ("honda", 1964, 1968, "honda_works_60s"),
    ("honda", 2006, 2008, "mercedes"),
    ("mercedes", 1954, 1955, "mercedes_works_50s"),
    ("mercedes", 2010, 2025, "mercedes"),
    ("alfa", 1950, 1951, "alfa_romeo_works"),
    ("alfa", 1979, 1985, "alfa_romeo_works"),
    ("alfa", 2019, 2023, "sauber"),
    ("aston_martin", 1959, 1960, "aston_martin_works_50s"),
    ("aston_martin", 2021, 2025, "aston_martin"),
    ("lola", 1962, 1963, "lola_60s"),
    ("lola", 1987, 1991, "larrousse"),
    ("lola", 1993, 1993, "scuderia_italia"),
    ("lola", 1997, 1997, "lola_1997"),
]

# 3) Châssis-moteur des années 50-60 (ex : lotus_climax -> team_lotus)
_ENGINE_SUFFIX = re.compile(r"^([a-z_]+)-[a-z_]+$")
_CHASSIS_TO_TEAM = {
    "lotus": "team_lotus",
    "brabham": "brabham",
    "cooper": "cooper",
    "mclaren": "mclaren",
    "matra": "matra",
    "eagle": "eagle",
    "march": "march",
    "de_tomaso": "de_tomaso",
    "lola": "lola_60s",
    "brm": "brm",
}


def resolve_team(constructor_id: str, season: int) -> str:
    """Retourne la clé unique d'écurie pour un constructor_id et une saison."""
    if not constructor_id or pd.isna(constructor_id):
        return "unknown"

    cid = str(constructor_id).strip().lower()

    # 1) Filtrage par années pour les IDs ambigus
    for item_id, y0, y1, cannon in LINEAGE_BY_YEAR:
        if item_id == cid and y0 <= season <= y1:
            return cannon

    # 2) Dictionnaire simple
    if cid in TEAM_LINEAGE:
        return TEAM_LINEAGE[cid]

    # 3) Nettoyage des identifiants châssis-moteur
    m = _ENGINE_SUFFIX.match(cid)
    if m and m.group() in _CHASSIS_TO_TEAM:
        return _CHASSIS_TO_TEAM[m.group(1)]

    return cid


def clean_raw_data() -> None:
    """Lit la table raw dans SQLite, effectue le nettoyage et créé la table cleaned."""
    with sqlite3.connect(config.DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM raw", conn)

    if df.empty:
        print("La table 'raw' est vide. Lancez d'abord get_data.py.")
        return

    # 1) Résolution de la clé d'écurie canonique
    df["team_key"] = df.apply(
        lambda r: resolve_team(r["constructor_id"], int(r["season"])), axis = 1
    )

    # 2) Conversion des dates
    df["race_date"] = pd.to_datetime(df["race_date"])
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])

    # 3) Calcul de l'âge exact du pilote au jour de la course (en années)
    df["age_at_race"] = (df["race_date"] - df["date_of_birth"]).dt.days / 365.25
    df["age_at_race"] = df["age_at_race"].round()

    # 4) Typage numérique pour plotly et dash
    for col in ["position", "grid", "points", "lat", "long"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5) Formatage ISO des dates pour SQLite
    df["race_date"] = df["race_date"].dt.strftime("%Y-%m-%d")
    df["date_of_birth"] = df["date_of_birth"].dt.strftime("%Y-%m-%d")

    # 6) Sauvegarde dans la table cleaned
    with sqlite3.connect(config.DB_PATH) as conn:
        df.to_sql("cleaned", conn, if_exists="replace", index=False)

    print(f"Table 'cleaned' générée avec succès ({len(df)} lignes nettoyées).")


if __name__ == "__main__":
    clean_raw_data()
