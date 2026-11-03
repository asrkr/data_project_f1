"""Composant du pied de page du dashboard."""
from dash import html


def footer() -> html.Footer:
    """Retourne le pied de page commun à toutes les pages."""
    return html.Footer(
        html.P("F1 Dashboard 1950-2025 - Projet Data"),
        style={"marginTop": "40px", "textAlign": "center"},
    )