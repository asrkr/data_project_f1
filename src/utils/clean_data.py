import sqlite3
import pandas as pd
import config


def clean_raw_data() -> None:
    """Lit la table raw dans SQLite, effectue le nettoyage et créé la table cleaned."""
    with sqlite3.connect(config.DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM raw", conn)

    if df.empty:
        print("La table 'raw' est vide. Lancez d'abord get_data.py.")
        return

    # Conversion des dates en datetime pour les calculs
    df["race_date"] = pd.to_datetime(df["race_date"])
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])

    # Calcul de l'âge exact du pilote au jour de la course (en années)
    df["age_at_race"] = (df["race_date"] - df["date_of_birth"]).dt.days / 365.25
    df["age_at_race"] = df["age_at_race"].round()

    # Typage numérique pour Plotly et Dash
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["long"] = pd.to_numeric(df["long"], errors="coerce")

    # Reconversion des dates en chaînes de caractères pour SQLite
    df["race_date"] = df["race_date"].dt.strftime("%Y-%m-%d")
    df["date_of_birth"] = df["date_of_birth"].dt.strftime("%Y-%m-%d")

    # Sauvegarde dans la table cleaned
    with sqlite3.connect(config.DB_PATH) as conn:
        df.to_sql("cleaned", conn, if_exists="replace", index=False)

    print(f"Table 'cleaned' générée avec succès ({len(df)} lignes nettoyées).")


if __name__ == "__main__":
    clean_raw_data()
