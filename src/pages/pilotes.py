"""Page d'analyse de l'âge des pilotes, filtrable par décennie."""
import dash
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from src.components.figures import build_age_histogram
from src.utils.common_functions import load_cleaned

dash.register_page(__name__, path="/pilotes", name="Âge des pilotes", order=1)

DECADES = range(1950, 2030, 10)

layout = html.Div(
    [
        html.H1("L'âge des pilotes"),
        html.P(
            "Choisis une décennie : l'histogramme rouge montre l'âge des pilotes "
            "à chaque course de cette période, comparé en gris à toute l'histoire "
            "de la F1 depuis 1950."
        ),
        dcc.Tabs(
            id = "pilotes-decade",
            value = "2020",
            children = [
                dcc.Tab(label=f"{decade}s", value=str(decade)) for decade in DECADES
            ],
            colors = {"border": "#dddddd", "primary": "#e10600", "background": "#f9f9f9"},
        ),
        dcc.Checklist(
            id = "pilotes-winners",
            options = [{"label": " Vainquers uniquement", "value": "winners"}],
            value = [],
            className = "winners-checklist",
        ),
        dcc.Graph(id="pilotes-age-hist")
    ]
)


@callback(
    Output("pilotes-age-hist", "figure"),
    Input("pilotes-decade", "value"),
    Input("pilotes-winners", "value"),
)
def update_age_histogram(decade: str, winners: list[str]) -> go.Figure:
    """Met à jour l'histogramme selon la décennie et la case cochée."""
    return build_age_histogram(load_cleaned(), int(decade), "winners" in winners)
