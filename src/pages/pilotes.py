"""Page d'analyse de l'âge des pilotes filtrable par décennie."""
import dash
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from src.components.figures import build_age_histogram
from src.utils.common_functions import load_cleaned

dash.register_page(__name__, path="/pilotes", name="Âge des pilotes")

DF_CLEANED = load_cleaned()

layout = html.Div(
    [
        html.H1("Distribution de l'âge des pilotes"),
        dcc.Dropdown(
            id="pilotes-decade-dropdown",
            options=[
                {"label": f"Décennie {dec}", "value": dec}
                for dec in range(1950, 2030, 10)
            ],
            value=2020,
            clearable=False,
        ),
        dcc.Graph(id="pilotes-age-hist"),
    ]
)


@callback(
    Output("pilotes-age-hist", "figure"),
    Input("pilotes-decade-dropdown", "value"),
)
def update_age_histogram(decade: int) -> go.Figure:
    """Filtre les données par décennie et met à jour l'histogramme."""
    filtered_df = DF_CLEANED[
        (DF_CLEANED["season"] >= decade) & (DF_CLEANED["season"] < decade + 10)
    ]
    return build_age_histogram(filtered_df)
