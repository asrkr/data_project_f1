"""Configuration centralisée du projet (chemins, API, cache, serveur)."""
from pathlib import Path

# Chemins (relatifs à la racine du dépôt)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR  / "db.sqlite"

# Clés d'accès et paramètres API Jolpica
API_BASE = "https://api.jolpi.ca/ergast/f1"
HEADERS = {"User-Agent": "ESIEE_DataProject_F1/1.0"}
PAGE_LIMIT = 100            # maximum accepté par Jolpica
PAUSE = 0.35                # > 0.25 s pour rester sous les 4 requêtes/s
MAX_ATTEMPTS = 8            # le quota horaire (500 requêtes/h) demande plus de 5 essais
MAX_BACKOFF = 60            # plafond d'attente par tentatives (secondes)

# Limites temporelles et cache
START_YEAR = 1950
END_YEAR = 2025
CACHE_MAX_AGE_DAYS = 7      # seule la dernière saison expire, les autres sont figées
INDY_LAST_SEASON = 1960     # Indy 500 au championnat de 1950 à 1960

# Serveur Dash
HOST = "127.0.0.1"
PORT = 8050
DEBUG = False
