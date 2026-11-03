"""Fonctions pures transformant un DataFrame en graphiques Plotly."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_age_histogram(df: pd.DataFrame, winners_only: bool = False) -> go.Figure:
    """Construit l'histogramme de l'âge des pilotes lors des courses."""
    clean_df = df.dropna(subset=["age_at_race"]).copy()

    if winners_only:
        clean_df = clean_df[clean_df["position"] == 1]

    fig = px.histogram(
        clean_df,
        x="age_at_race",
        nbins=30,
        title="Distribution de l'âge des pilotes en course",
        labels={"age_at_race": "Âge lors de la course"},
    )
    fig.update_layout(yaxis_title="Nombre de départs")
    return fig


def build_circuits_map(df: pd.DataFrame) -> go.Figure:
    """Carte des circuits : un point par circuit, taille = nombre de GP."""
    races = df.drop_duplicates(subset=["season", "round"])
    circuits = races.groupby("circuit_id", as_index=False).agg(
        circuit_name = ("circuit_name", "first"),
        country = ("country", "first"),
        lat = ("lat", "first"),
        long = ("long", "first"),
        nb_gp = ("round", "size"),
        first_season = ("season", "min"),
        last_season = ("season", "max"),
    )
    fig = px.scatter_map(
        circuits,
        lat = "lat",
        lon = "long",
        size = "nb_gp",
        hover_name = "circuit_name",
        hover_data = {
            "country": True,
            "nb_gp": True,
            "first_season": True,
            "last_season": True,
            "lat": False,
            "long": False,
        },
        labels = {
            "country": "Pays",
            "nb_gp": "Nombre de courses",
            "first_season": "Première saison",
            "last_season": "Dernière saison",
        },
        size_max = 25,
        color_discrete_sequence = ["#e10600"],
        opacity = 0.6,
        zoom = 1,
        map_style = "carto-positron",
        template = "plotly_white",
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    return fig
