"""Page d'acceuil : présentation du projet et chiffres clés."""

import dash
from dash import html

from src.utils.common_functions import load_cleaned

# order=0 place l'acceuil en premier dans la barre de navigation
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


def _figure_card(label: str, value: int) -> html.Div:
    """Construit une vignette affichant un chiffre clé et son libellé."""
    return html.Div(
        [html.H2(f"{value:,}".replace(",", " ")), html.P(label)],
        style={"textAlign": "center", "padding": "20px", "minWidth": "150px"},
    )
