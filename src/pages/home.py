"""Page d'accueil : présentation du projet, chiffres clés et accès aux pages."""

import dash
from dash import dcc, html

from src.components.figures import build_team_wins
from src.components.key_figures import figure_card
from src.utils.common_functions import load_cleaned

# order = 0 place l'accueil en premier dans la barre de navigation
dash.register_page(__name__, path="/", name="Accueil", order=0)

# Une phrase par page, pour les vignettes (clé = path de la page)
PAGE_BLURBS = {
    "/pilotes": "Répartition de l'âge des pilotes, décennie par décennie.",
    "/circuits": "Carte des circuits et fiche détaillée de chacun.",
}


def _key_figures() -> dict[str, int]:
    """Calcule les chiffres clés affichés en tête du dashboard."""
    df = load_cleaned()
    return {
        "Saisons": df["season"].nunique(),
        "Grands Prix": len(df.drop_duplicates(["season", "round"])),
        "Pilotes": df["driver_id"].nunique(),
        "Circuits": df["circuit_id"].nunique(),
    }


def _page_cards() -> list[dcc.Link]:
    """Une vignette cliquable par page du dashboard (sauf l'accueil)."""
    pages = sorted(dash.page_registry.values(), key=lambda p: p["order"])
    return [
        dcc.Link(
            html.Div(
                [
                    html.H3(page["name"]),
                    html.P(PAGE_BLURBS.get(page["path"], "")),
                ],
                className = "page-card",
            ),
            href = page["path"]
        )
        for page in pages
        if page["path"] != "/"
    ]


def layout(**_kwargs: object) -> html.Div:
    """Construit la page d'accueil (appelée par Dash à chaque affichage)."""
    df = load_cleaned()
    return html.Div(
        [
            html.H1("Formule 1 : 75 ans de résultats (1950-2025)"),
            html.P(
                "Ce dashboard explore l'histoire du championnat du monde de Formule 1 "
                "à partir des résultats de chaque Grand Prix depuis 1950 (données "
                "Jolpica/Ergast) : âge des pilotes, circuits visités et écuries."
            ),
            html.Div(
                [figure_card(label, value) for label, value in _key_figures().items()],
                className = "key-figures",
            ),
            html.H2("Explorer"),
            html.Div(_page_cards(), className="page-cards"),
            html.H2("Les écuries les plus victorieuses"),
            html.P(
                "Les victoires sont regroupées en suivant leurs renommages "
                "et rachats (par exemple Benetton, Renault et Alpine comptent pour "
                "une seule écurie)."
            ),
            dcc.Graph(
                figure = build_team_wins(df),
                config = {"displayModeBar": False},
            )
        ]
    )
