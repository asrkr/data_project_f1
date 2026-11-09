"""Fonctions pures transformant un DataFrame en graphiques Plotly."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.countries import country_fr

AGE_BINS = {"start": 15, "end": 60, "size": 1}

# Contours des pays (Natural Earth, domaine public) servis par Dash depuis assets/ :
# La carte fonctionne sans connexion internet
COUNTRIES_GEOJSON = "assets/geo/ne_50m_admin_0_countries.geojson"


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
        barmode = "overlay",
        template = "plotly_white",
        title = (
            f"Âge des pilotes dans les années {decade} "
            f"({'vainqueurs' if winners_only else 'tous les partants'}) "
            "comparé à 1950-2025"
        ),
        xaxis_title = "Âge au départ de la course (ans)",
        yaxis_title = "Part des participations (%)",
        legend = {"x": 0.99, "y": 0.99, "xanchor": "right", "yanchor": "top"},
        margin = {"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return fig


def build_circuits_map(df: pd.DataFrame, start: int, end: int) -> go.Figure:
    """Carte des circuits sur une période : un point par circuit, taille = nombre de courses."""
    races = df.drop_duplicates(subset=["season", "round"])
    period = races[races["season"].between(start, end)]
    circuits = period.groupby("circuit_id", as_index=False).agg(
        circuit_name = ("circuit_name", "first"),
        country = ("country", "first"),
        lat = ("lat", "first"),
        long = ("long", "first"),
        nb_gp = ("round", "count"),
    )
    circuits["country"] = circuits["country"].map(country_fr)
    fig = px.scatter_map(
        circuits,
        lat = "lat",
        lon = "long",
        size = "nb_gp",
        hover_name = "circuit_name",
        custom_data = ["circuit_id", "country", "nb_gp"],
        size_max = 25,
        color_discrete_sequence = ["#e10600"],
        opacity = 0.6,
        zoom = 1,
        center = {"lat": 30, "lon": 10},
        map_style = "white-bg",
        template = "plotly_white",
    )
    fig.update_traces(
        hovertemplate = (
            "<b>%{hovertext}</b> (%{customdata[1]})<br>"
            "%{customdata[2]} course(s) sur la période<br>"
            "<i>Cliquer pour voir la fiche</i><extra></extra>"
        )
    )
    fig.update_layout(
        margin = {"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor = "#dbe7f0",
        uirevision = "circuits-map",
        map_layers = [
            {
                "sourcetype": "geojson",
                "source": COUNTRIES_GEOJSON,
                "type": "fill",
                "color": "#f4f1ea",
                "below": "traces",
            },
            {
                "sourcetype": "geojson",
                "source": COUNTRIES_GEOJSON,
                "type": "line",
                "color": "#cfcac0",
                "line": {"width": 1},
                "below": "traces",
            },
        ],
    )
    return fig


def _years(seasons: pd.Series[int]) -> str:
    """Liste des saisons triées, sous forme de texte : "1954, 1955, 1957"."""
    return ", ".join(str(year) for year in sorted(seasons))


def split_first_places(
    df: pd.DataFrame, circuit_id: str, column: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pilotes classés 1ers sur un circuit (column = "position" ou "grid").
    Renvoie (au moins 2 vicroires, triés par nombre) et (une seule victoire, triés par année)
    """
    firsts = df[(df["circuit_id"] == circuit_id) & (df[column] == 1)]
    counts = (
        firsts.groupby("driver_name", as_index=False)
        .agg(count=("season", "size"), years=("season", _years))
        .sort_values("count", ascending=False)
    )
    regulars = counts[counts["count"] >= 2]
    once = counts[counts["count"] == 1].sort_values("years")
    return regulars, once


def pole_win_rate(df: pd.DataFrame, circuit_id: str | None = None) -> float:
    """Part (%) des victoires obtenues en partant 1er sur la grille.
    Sans circuit_id, le taux est calculé sur tous les circuits.
    """
    wins = df[df["position"] == 1]
    if circuit_id is not None:
        wins = wins[wins["circuit_id"] == circuit_id]
    if wins.empty:
        return 0.0
    return round(float((wins["grid"] == 1).mean()) * 100, 1)


def build_circuit_top(counts: pd.DataFrame, label: str) -> go.Figure:
    """Barres horizontales des pilotes classés 1ers au moins 2 fois."""
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
        xaxis = {"dtick": 1, "title": label},
        yaxis = {"categoryorder": "total ascending"},
        margin = {"l": 0, "r": 0, "t": 10, "b": 40},
        height = 80 + 30 * len(counts),
    )
    return fig


def build_team_wins(df: pd.DataFrame, top: int = 10) -> go.Figure:
    """Barres horizontales des écuries les plus victorieuses, regroupées
    par team_key."""
    wins = df[df["position"] == 1]
    labels = (
        wins.sort_values("season")
        .groupby("team_key")["team_name"]
        .last()
    )
    counts = (
        wins.groupby("team_key")
        .size()
        .rename("wins")
        .reset_index()
        .nlargest(top, "wins")
        .sort_values("wins")
    )
    counts["team"] = counts["team_key"].map(labels)
    fig = px.bar(
        counts,
        x = "wins",
        y = "team",
        orientation = "h",
        title = f"Top {top} des écuries par victoires en Grand Prix (1950-2025)",
        labels = {"wins": "Victoires", "team": "Écurie"},
        color_discrete_sequence = ["#e10600"],
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    return fig
