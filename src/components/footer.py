"""Composant du pied de page du dashboard."""

from dash import html


def footer() -> html.Footer:
    """Retourne le pied de page commun à toutes les pages, avec
    la source des données."""
    return html.Footer(
        [
            html.P("F1 Dashboard 1950-2025 - Ayan Sarkar et Antoine Palliser - ESIEE Paris"),
            html.P(
                [
                    " Données : ",
                    html.A(
                        "API Jolpica F1",
                        href = "https://api.jolpi.ca/ergast/",
                        target = "_blank",      # nouvel onglet à l'ouverture
                    ),
                ]
            ),
        ],
    )
