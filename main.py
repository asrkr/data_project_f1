"""Point d'entrée : prépare les données si nécessaire, puis lance le dashboard."""
import argparse
import logging

import config
from src.app import create_app
from src.utils.clean_data import clean_raw_data
from src.utils.common_functions import table_exists
from src.utils.get_data import update_raw_database


def main() -> None:
    """Construit la base si elle est absente (ou sur demande), puis démarre le serveur."""
    parser = argparse.ArgumentParser(description="Dashboard F1 1950-2025")
    parser.add_argument(
        "--refresh", action="store_true", help="met à jour les données depuis l'API"
    )
    args = parser.parse_args()

    if args.refresh or not table_exists("cleaned"):
        update_raw_database()
        clean_raw_data()

    # Le serveur de développement (werkzeug) affiche un avertissement au lancement :
    # On ne garde que les erreurs pour que la console reste propre.
    # Aucun warning à l'exécution.
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
