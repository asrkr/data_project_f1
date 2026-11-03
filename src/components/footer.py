"""Composant de la barre de navigation générée automatiquement."""
import dash
from dash import dcc, html


def navbar() -> html.Nav:
    """Génère les liens de navigation à partir des pages enregistrées dans Dash."""
    return html.Nav(
        [
            # Parcourt chaque page détectée par Dash et crée un lien cliquable
            dcc.Link(
                page["name"],
                href=page["relative_path"],
                style={"marginRight": "15px"},
            )
            for page in dash.page_registry.values()
        ]
    )