"""Traduction en français des noms de pays fournis par l'API (en anglais)."""

# Seuls les pays dont le nom change sont listés : les autres (Canada, France, 
# Monaco, Portugal, Qatar) sont renvoyés tels quel par country_fr().
COUNTRIES_FR: dict[str, str] = {
    "Argentina": "Argentine",
    "Australia": "Australie",
    "Azerbaijan": "Azerbaïdjan",
    "Bahrain": "Bahreïn",
    "Belgium": "Belgique",
    "Brazil": "Brésil",
    "China": "Chine",
    "Germany": "Allemagne",
    "Hungary": "Hongrie",
    "India": "Inde",
    "Italy": "Italie",
    "Japan": "Japon",
    "Korea": "Corée du Sud",
    "Malaysia": "Malaisie",
    "Mexico": "Mexique",
    "Morocco": "Maroc",
    "Netherlands": "Pays-Bas",
    "Russia": "Russie",
    "Saudi Arabia": "Arabie saoudite",
    "Singapore": "Singapour",
    "South Africa": "Afrique du Sud",
    "Spain": "Espagne",
    "Sweden": "Suède",
    "Switzerland": "Suisse",
    "Turkey": "Turquie",
    "UAE": "Émirats arabes unis",
    "UK": "Royaume-Uni",
    "USA": "États-Unis",
}


def country_fr(name: str) -> str:
    """Renvoie le nom français du pays, ou le nom d'origine s'il est inconnu."""
    return COUNTRIES_FR.get(name, name)
