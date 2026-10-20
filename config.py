import os


# Chemins essentiels pour le projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "db.sqlite")

# Clés d'accès et paramètres API Jolpica
API_BASE = "https://api.jolpi.ca/ergast/f1"
HEADERS = {"User-Agent": "ESIEE_DataProject_F1/1.0"}
PAGE_LIMIT = 100
PAUSE = 0.35    # Pause entre les requêtes

# Limites temporelles pour le dataset
START_YEAR = 1950
END_YEAR = 2025
