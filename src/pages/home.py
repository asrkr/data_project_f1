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
        className = "key-figure",
    )


layout = html.Div(
    [
        html.H1("Formule 1 : 75 ans de résultats (1950-2025)"),
        html.P(
            "Ce dashboard explore l'histoire du championnat du monde de Formule 1 "
            "à partir des résultats de chaque Grand Prix : âge des pilotes, "
            "circuits visités et évolution des saisons."
        ),
        html.Div(
            [_figure_card(label, value) for label, value in _key_figures().items()],
            className = "key-figures",
        ),
    ]
)
