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