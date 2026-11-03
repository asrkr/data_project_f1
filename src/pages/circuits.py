"""Page de la carte des circuits."""

import dash
from dash import dcc, html

from src.components.figures import build_circuits_map
from src.utils.common_functions import load_cleaned

dash.register_page(__name__, path="/circuits", name="Circuits", order=2)


def layout(**_kwargs: object) -> html.Div:
    """Construit la pageà chaque visite, à partir de la table cleaned."""
    df = load_cleaned()
    return html.Div(
        [
            html.H1("Les circuits de Formule 1"),
            html.P(
                "Chaque point est un circuit qui a accueilli au moins un Grand Prix "
                "depuis 1950. Plus le point est gros, plus le circuit a accueilli de courses."
                " Survole un point pour voir le détail."
            ),
            dcc.Graph(
                figure = build_circuits_map(df),
                config = {"scrollZoom": True},
                className = "mapGraph",
            ),
        ]
    )
