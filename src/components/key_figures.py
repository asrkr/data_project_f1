"""Vignette affichant un chiffre clé, partagée par plusieurs pages."""

from dash import html


def figure_card(label: str, value: int | str) -> html.Div:
    """Construit une vignette : le chiffre en grand, son libellé en dessous."""
    text = f"{value:,}".replace(",", " ") if isinstance(value, int) else value
    return html.Div([html.H2(text), html.P(label)], className="key-figure")
