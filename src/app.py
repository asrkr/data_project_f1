"""Création de l'application Dash multi-pages."""
from dash import Dash, html, page_container

from src.components.footer import footer
from src.components.navbar import navbar


def create_app() -> Dash:
    """Crée l'application et le layout commun à toutes les pages."""
    app = Dash(
        __name__,
        use_pages=True,  # charge src/pages/*.py
        suppress_callback_exceptions=True,
        title="F1 Dashboard 1950-2025",
    )
    app.layout = html.Div([navbar(), page_container, footer()])
    return app