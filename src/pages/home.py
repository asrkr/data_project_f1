"""Page d'accueil : présentation du projet et chiffres clés."""

import dash
from dash import html

from src.components.key_figures import figure_card
from src.utils.common_functions import load_cleaned

# order=0 place l'accueil en premier dans la barre de navigation
dash.register_page(__name__, path="/", name="Accueil", order=0)


def _key_figures() -> dict[str, int]:
    """Calcule les chiffres clés affichés en tête du dashboard."""
    df = load_cleaned()
    return {
        "Saisons": df["season"].nunique(),
        "Grands Prix": len(df.drop_duplicates(["season", "round"])),
        "Pilotes": df["driver_id"].nunique(),
        "Circuits": df["circuit_id"].nunique(),
    }


def layout(**_kwargs: object) -> html.Div:
    """Construit la page d'accueil (appelée par Dash à chaque affichage)."""
    return html.Div(
        [
            html.H1("Formule 1 : 75 ans de résultats (1950-2025)"),
            html.P(
                "Ce dashboard explore l'histoire du championnat du monde de Formule 1"
                "à partir des résultats de chaque Grand Prix : âge des pilotes, "
                "circuits visités et évolution des saisons."
            ),
            html.Div(
                [figure_card(label, value) for label, value in _key_figures().items()],
                className = "key-figures",
            ),
        ]
    )
