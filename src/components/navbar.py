"""Composant de la barre de navigation générée automatiquement."""
import dash
from dash import Input, Output, callback, dcc, html


def navbar() -> html.Nav:
    """Génère les liens de navigation à partir des pages enregistrées dans Dash."""
    return html.Nav(
        [
            dcc.Link(
                page["name"],
                href = page["relative_path"],
                id = {"type": "nav-link", "path": page["relative_path"]},
            )
            for page in dash.page_registry.values()
        ],
        className = "navbar",
    )


@callback(
    Output({"type": "nav-link", "path": dash.ALL}, "className"),
    Input("_pages_location", "pathname"),
)
def highlight_active_link(pathname: str) -> list[str]:
    """Ajoute la classe 'active' au lien de la page affichée."""
    return [
        "active" if page["relative_path"] == pathname else ""
        for page in dash.page_registry.values()
    ]
