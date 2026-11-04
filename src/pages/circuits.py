"""Page de la carte des circuits, filtrable par période."""

import dash
import pandas as pd
from dash import Input, Output, Patch, callback, dcc, html

from src.components.figures import build_circuits_map
from src.utils.common_functions import load_cleaned

dash.register_page(__name__, path="/circuits", name="Circuits", order=2)


def _summary(df: pd.DataFrame, start: int, end: int) -> str:
    """Phrase résumant le nombre de circuits et GP sur la période."""
    races = df[df["season"].between(start, end)].drop_duplicates(
        subset = ["season", "round"]
    )
    return (
        f"De {start} à {end} : {races['circuit_id'].nunique()} circuits, "
        f"{len(races)} Grands Prix."
    )


def layout(**_kwargs: object) -> html.Div:
    """Construit la page avec la carte complète et le curseur de période."""
    df = load_cleaned()
    first, last = int(df["season"].min()), int(df["season"].max())
    marks = {year: str(year) for year in range(first, last+1, 10)}
    marks[last] = str(last)
    return html.Div(
        [
            html.H1("Les circuits de Formule 1."),
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
            html.P(
                _summary(df, first, last),
                id = "circuits-summary",
                className = "map-summary",
            ),
            dcc.Graph(
                id = "circuits-map",
                figure = build_circuits_map(df, first, last),
                config = {"scrollZoom": True},
                className = "map-graph",
            ),
        ]
    )


@callback(
    Output("circuits-map", "figure"),
    Output("circuits-summary", "children"),
    Input("circuits-period", "value"),
    prevent_initial_call = True,
)
def update_map(period: list[int]) -> tuple[Patch, str]:
    """Remplace seulement les points de la carte : le zoom est conservé."""
    start, end = period
    df = load_cleaned()
    patched = Patch()
    patched["data"] = build_circuits_map(df, start, end).to_dict()["data"]
    return patched, _summary(df, start, end)
