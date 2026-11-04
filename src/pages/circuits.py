"""Page de la carte des circuits, filtrable par période."""

import dash
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from src.components.figures import build_circuits_map
from src.utils.common_functions import load_cleaned

dash.register_page(__name__, path="/circuits", name="Circuits", order=2)


def layout(**_kwargs: object) -> html.Div:
    """Construit la page avec un curseur couvrant toutes les saisons disponibles."""
    df = load_cleaned()
    first, last = int(df["season"].min()), int(df["season"].max())
    marks = {year: str(year) for year in range(first, last + 1, 10)}
    marks[last] = str(last)
    return html.Div(
        [
            html.H1("Les circuits de Formule 1"),
            html.P(
                "Choisis une période avec le curseur : chaque point est un circuit "
                "qui a accueilli au moins un Grand Prix pendant cette période. "
                "Plus le point est gros, plus il a accueilli de courses. "
                "Survole un point pour voir le détail."
            ),
            dcc.RangeSlider(
                id = "circuits-period",
                min = first,
                max = last,
                step = 1,
                value = [first, last],
                marks = marks,
            ),
            html.P(id="circuits-summary", className="map-summary"),
            dcc.Graph(
                id = "circuits-map",
                config = {"scrollZoom": True},
                className = "map-graph",
            )
        ]
    )


@callback(
    Output("circuits-map", "figure"),
    Output("circuits-summary", "children"),
    Input("circuits-period", "value"),
)
def update_map(period: list[int]) -> tuple[go.Figure, str]:
    """Met à jour la carte et le résumé selon la période choisie."""
    start, end = period
    df = load_cleaned()
    races = df[df["season"].between(start, end)].drop_duplicates(
        subset = ["season", "round"]
    )
    summary = (
        f"De {start} à {end} : {races['circuit_id'].nunique()} circuits, "
        f"{len(races)} Grands Prix."
    )
    return build_circuits_map(df, start, end), summary
