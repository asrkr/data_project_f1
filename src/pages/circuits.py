"""Page de la carte des circuits, filtrable par période."""

from typing import Any

import dash
import pandas as pd
from dash import Input, Output, Patch, callback, dcc, html

from src.components.figures import build_circuit_top, build_circuits_map, split_first_places
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
            html.Div(
                html.P("Clique sur un circuit de la carte pour afficher sa fiche."),
                id = "circuits-details",
                className = "circuit-card",
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


def _first_places_block(
    df: pd.DataFrame, circuit_id: str, column: str, label: str, once_text: str
) -> html.Div:
    """Barres pour les pilotes classés 1ers au moins 2 fois, étiquettes pour les autres."""
    regulars, once = split_first_places(df, circuit_id, column)
    children: list[Any] = []
    if not regulars.empty:
        children.append(
            dcc.Graph(
                figure = build_circuit_top(regulars, label),
                config = {"displayModeBar": False},
            )
        )
    if not once.empty:
        children.append(html.P(once_text, className="tags-title"))
        children.append(
            html.Div(
                [
                    html.Span(f"{row.driver_name} · {row.years}", className="tag")
                    for row in once.itertuples()
                ],
                className = "tags",
            )
        )
    return html.Div(children)


@callback(
    Output("circuits-details", "children"),
    Input("circuits-map", "clickData"),
    prevent_initial_call = True,
)
def show_circuit(click: dict[str, Any] | None) -> html.Div:
    """Affiche la fiche du circuit cliqué (pour toute son histoire)."""
    if not click:
        return html.Div(html.P("Clique sur un circuit de la carte."))
    circuit_id = str(click["points"][0]["customdata"][0])
    df = load_cleaned()
    races = df[df["circuit_id"] == circuit_id].drop_duplicates(
        subset = ["season", "round"]
    )
    info = races.iloc[0]
    return html.Div(
        [
            html.H2(f"{info['circuit_name']} ({info['country']})"),
            html.P(
                f"{len(races)} Grands Prix entre {races['season'].min()} "
                f"et {races['season'].max()}."
            ),
            html.H3("Pilotes les plus victorieux sur ce circuit"),
            _first_places_block(
                df, circuit_id, "position", "Victoires", "Une victoire ici :"
            ),
        ]
    )
