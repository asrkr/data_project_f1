"""Tests de la page Circuits : fonctions de calcul et callbacks, sans serveur."""

import dash
import pandas as pd
import pytest
from dash import Patch, html

from src.pages import circuits, home, pilotes
from src.pages.circuits import (
    _circuit_figures,
    _summary,
    layout,
    show_circuit,
    update_map,
)
from src.pages.home import _key_figures, _page_cards

MONACO_CLICK = {"points": [{"customdata": ["monaco", "Monaco", 3]}]}


@pytest.fixture
def fake_db(monkeypatch: pytest.MonkeyPatch, df: pd.DataFrame) -> None:
    """La page lit le mini-jeu de données au lieu de la base SQLite."""
    monkeypatch.setattr(circuits, "load_cleaned", lambda: df)


def test_circuits_page_registered() -> None:
    """La page est enregistrée sur /circuits."""
    paths = {page["path"] for page in dash.page_registry.values()}
    assert "/circuits" in paths


def test_summary(df: pd.DataFrame) -> None:
    """Résumé : circuits et GP comptés sur la période seulement."""
    assert _summary(df, 1950, 1953) == "De 1950 à 1953 : 2 circuits, 4 Grands Prix."
    assert _summary(df, 1951, 1951) == "De 1951 à 1951 : 1 circuits, 1 Grands Prix."


def test_circuit_figures(df: pd.DataFrame) -> None:
    """Chiffres clés de Monaco sur le mini-jeu de données."""
    figures = _circuit_figures(df, "monaco")
    assert figures["Grands Prix"] == 3
    assert figures["Années d'activité"] == "1950-1953"
    assert figures["Vainqueurs différents"] == 2
    assert figures["Polemen différents"] == 2
    assert figures["Pole → victoire (moy. F1 50,0 %)"] == "66,7 %"


@pytest.mark.usefixtures("fake_db")
def test_layout_contains_slider_and_map() -> None:
    """Le layout contient le curseur et la carte."""
    page = str(layout())
    assert "circuits-period" in page
    assert "circuits-map" in page


@pytest.mark.usefixtures("fake_db")
def test_update_map_returns_patch_and_summary() -> None:
    """Le callback renvoie un Patch et le résumé de la période."""
    patched, summary = update_map([1950, 1950])
    assert isinstance(patched, Patch)
    assert summary == "De 1950 à 1950 : 1 circuits, 1 Grands Prix."


@pytest.mark.usefixtures("fake_db")
def test_show_circuit_card() -> None:
    """La fiche affiche le nom du circuit et la période."""
    card = str(show_circuit(MONACO_CLICK, [1950, 1953]))
    assert "Circuit de Monaco (Monaco)" in card
    assert "1950-1953" in card


@pytest.mark.usefixtures("fake_db")
def test_show_circuit_outside_period() -> None:
    """Circuit sans GP sur la période : message, pas d'erreur."""
    card = str(show_circuit(MONACO_CLICK, [1951, 1951]))
    assert "n'a pas accueilli" in card


def test_show_circuit_without_click() -> None:
    """Sans clic, invitation à cliquer."""
    result = show_circuit(None, [1950, 2025])
    assert isinstance(result, html.Div)
    assert "Clique" in str(result)


# --- Page Pilotes ---------------------------------------------------------


def test_pilotes_page_registered() -> None:
    """La page est enregistrée sur /pilotes."""
    paths = {page["path"] for page in dash.page_registry.values()}
    assert "/pilotes" in paths


def test_pilotes_layout_has_one_tab_per_decade() -> None:
    """Un onglet par décennie de 1950 à 2020."""
    page = str(pilotes.layout)
    assert "pilotes-decade" in page
    assert page.count("value='") >= len(list(pilotes.DECADES))


def test_update_age_histogram(
    monkeypatch: pytest.MonkeyPatch, ages: pd.DataFrame
) -> None:
    """Le callback renvoie l'histogramme de la décennie choisie."""
    monkeypatch.setattr(pilotes, "load_cleaned", lambda: ages)
    fig = pilotes.update_age_histogram("1950", [])
    assert fig.data[1].name == "Années 1950"
    assert list(fig.data[1].x) == [25.0, 30.5]
    fig = pilotes.update_age_histogram("1960", ["winners"])
    assert list(fig.data[0].x) == [25.0, 40.0]


# --- Page Accueil ---------------------------------------------------------


def test_home_page_registered() -> None:
    """L'accueil est enregistré sur /."""
    paths = {page["path"] for page in dash.page_registry.values()}
    assert "/" in paths


def test_home_key_figures(monkeypatch: pytest.MonkeyPatch, df: pd.DataFrame) -> None:
    """Chiffres clés calculés sur le mini-jeu de données."""
    monkeypatch.setattr(
        home, "load_cleaned", lambda: df.assign(driver_id=df["driver_name"])
    )
    assert _key_figures() == {
        "Saisons": 4,
        "Grands Prix": 4,
        "Pilotes": 2,
        "Circuits": 2,
    }


def test_home_page_cards_link_to_other_pages() -> None:
    """Une vignette par page enregistrée, sauf l'accueil."""
    cards = _page_cards()
    hrefs = {card.href for card in cards}
    assert "/" not in hrefs
    assert {"/pilotes", "/circuits"} <= hrefs
