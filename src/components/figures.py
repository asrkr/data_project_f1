"""Fonctions pures transformant un DataFrame en graphiques Plotly."""
import pandas as pd
import plotly.graph_objects as go

AGE_BINS = {"start": 15, "end": 60, "size": 1}


def build_age_histogram(df: pd.DataFrame, decade: int, winners_only: bool = False) -> go.Figure:
    """Histogramme de l'âge : décennie choisie (rouge) sur toute l'histoire (gris)"""
    data = df[df["position"] == 1] if winners_only else df
    period = data[(data["season"] >= decade) & (data["season"] < decade + 10)]

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x = data["age_at_race"],
            name = "1950-2025",
            histnorm = "percent",
            xbins = AGE_BINS,
            marker_color = "#c8c8c8",
        )
    )
    fig.add_trace(
        go.Histogram(
            x = period["age_at_race"],
            name = f"Années {decade}",
            histnorm = "percent",
            xbins = AGE_BINS,
            marker_color = "#e10600",
            opacity = 0.75,
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
        xaxis_title = "Âge au départ de la course (ans)",
        yaxis_title = "Part des participations (ans)",
        legend = {"orientation": "h", "y": 1.1},
        margin = {"l": 40, "r": 20, "t": 40, "b": 40},
    )
    return fig
