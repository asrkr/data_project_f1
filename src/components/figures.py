"""Fonctions pures transformant un DataFrame en graphiques Plotly."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

AGE_BINS = {"start": 15, "end": 60, "size": 1}
TOP_MAX = 10
TOP_MIN = 3
TOP_FALLBACK = 5


def build_age_histogram(
    df: pd.DataFrame, decade: int, winners_only: bool = False
) -> go.Figure:
    """Histogramme de l'âge : décennie choisie (rouge) sur toute l'histoire (gris)."""
    data = df[df["position"] == 1] if winners_only else df
    period = data[(data["season"] >= decade) & (data["season"] < decade + 10)]

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=data["age_at_race"],
            name="1950-2025",
            histnorm="percent",
            xbins=AGE_BINS,
            marker_color="#c8c8c8",
        )
    )
    fig.add_trace(
        go.Histogram(
            x=period["age_at_race"],
            name=f"Années {decade}",
            histnorm="percent",
            xbins=AGE_BINS,
            marker_color="#e10600",
            opacity=0.75,
        )
    )
    fig.update_traces(
        hovertemplate=(
            "Âge : %{x} ans<br>"
            "%{y:.1f} % des participations"
            "<extra>%{fullData.name}</extra>"
        )
    )
    fig.update_layout(
        barmode="overlay",
        template="plotly_white",
        xaxis_title="Âge au départ de la course (ans)",
        yaxis_title="Part des participations (%)",
        legend={"orientation": "h", "y": 1.1},
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
    )
    return fig


def build_circuits_map(df: pd.DataFrame, start: int, end: int) -> go.Figure:
    """Carte des circuits sur une période : un point par circuit, taille = nombre de GP."""
    races = df.drop_duplicates(subset=["season", "round"])
    races = races.assign(
        first_season=races.groupby("circuit_id")["season"].transform("min"),
        last_season=races.groupby("circuit_id")["season"].transform("max"),
    )
    period = races[races["season"].between(start, end)]
    circuits = period.groupby("circuit_id", as_index=False).agg(
        circuit_name=("circuit_name", "first"),
        country=("country", "first"),
        lat=("lat", "first"),
        long=("long", "first"),
        nb_gp=("round", "size"),
        first_season=("first_season", "first"),
        last_season=("last_season", "first"),
    )
    fig = px.scatter_map(
        circuits,
        lat="lat",
        lon="long",
        size="nb_gp",
        hover_name="circuit_name",
        custom_data = ["circuit_id"],
        hover_data={
            "country": True,
            "nb_gp": True,
            "first_season": True,
            "last_season": True,
            "lat": False,
            "long": False,
        },
        labels={
            "country": "Pays",
            "nb_gp": "Courses sur la période",
            "first_season": "Première saison",
            "last_season": "Dernière saison",
        },
        size_max=25,
        color_discrete_sequence=["#e10600"],
        opacity=0.6,
        zoom=1,
        map_style="carto-positron",
        template="plotly_white",
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        uirevision="circuits-map",
    )
    return fig


def _years(seasons: pd.Series[int]) -> str:
    """Liste des saisons triées, sous forme de texte : "1954, 1955, 1957"."""
    return ", ".join(str(year) for year in sorted(seasons))


def _top_drivers(df: pd.DataFrame, circuit_id: str, column: str) -> pd.DataFrame:
    """Pilotes classés 1ers sur un circuit (column = "position" ou "grid")
    On garde ceux qui l'ont fait au moins 2 fois, TOP_MAX (10) au maximum.
    S'il y en a moins de TOP_MIN (3), on affiche le TOP_FALLBACK (5) pour
    ne pas avoir un graphique vide.
    """
    firsts = df[(df["circuit_id"] == circuit_id) & (df[column] == 1)]
    counts = (
        firsts.groupby("driver_name", as_index=False)
        .agg(count=("season", "size"), years=("season", _years))
        .sort_values("count", ascending=False)
    )
    regulars = counts[counts["count"] >= 2]
    if len(regulars) < TOP_MIN:
        return counts.head(TOP_FALLBACK)
    return regulars.head(TOP_MAX)


def build_circuit_top(df: pd.DataFrame, circuit_id: str, column: str, label: str) -> go.Figure:
    """Barres horizontales : pilotes les plus souvent 1ers sur un circuit."""
    counts = _top_drivers(df, circuit_id, column)
    fig = px.bar(
        counts,
        x = "count",
        y = "driver_name",
        orientation = "h",
        custom_data = ["years"],
        labels = {"count": label, "driver_name": ""},
        color_discrete_sequence = ["#e10600"],
        template = "plotly_white",
    )
    fig.update_traces(
        hovertemplate = (
            "%{y} : %{x} " + label.lower() + "<br>"
            "%{customdata[0]}<extra></extra>"
        )
    )
    fig.update_layout(
        xaxis = {"dtick": 1},
        yaxis = {"categoryorder": "total ascending"},
        margin = {"l": 0, "r": 0, "t": 10, "b": 40},
        height = 300,
    )
    return fig
