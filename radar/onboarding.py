# radar/onboarding.py
"""Moteur conversationnel à base de règles pour l'assistant Radar (🎯)."""

from __future__ import annotations
import re
from datetime import date
from typing import Dict, Any, List, Tuple

from radar.models import Profile

AVAILABLE_INTERESTS: List[str] = [
    "quant",
    "markets",
    "investment_banking",
    "asset_management",
    "fintech",
    "venture_capital",
    "ai",
    "startups",
    "corporate_finance",
    "tech",
]

INTEREST_LABELS_FR: Dict[str, str] = {
    "quant": "Quant & Recherche quantitative",
    "markets": "Marchés financiers (Sales & Trading)",
    "investment_banking": "Banque d'investissement (M&A / ECM / DCM)",
    "asset_management": "Gestion d'actifs & Portefeuille",
    "fintech": "Fintech & Paiements",
    "venture_capital": "Capital de risque (VC)",
    "ai": "Intelligence artificielle & Data",
    "startups": "Startups & Produit",
    "corporate_finance": "Finance d'entreprise & Crédit",
    "tech": "Tech & Génie logiciel",
}

QUESTIONS: List[str] = [
    "Salut ! Je suis **Radar** 🎯. En 5 questions rapides, je vais filtrer les programmes auxquels tu es *vraiment* admissible.\n\n**Question 1/5 :** En quelle année d'études universitaires es-tu actuellement ? *(ex: 1, 2, 3 ou 4)*",
    "Noté ! **Question 2/5 :** Quelle est ta date prévue de diplomation ? *(format AAAA-MM, ex: 2029-05 ou Mai 2029)*",
    "Parfait. **Question 3/5 :** Quels sont tes domaines d'intérêt ?\nTu peux écrire plusieurs mots-clés séparés par une virgule parmi : `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance`, `tech` *(ou tape « tous »)*.",
    "Bien reçu. **Question 4/5 :** Quelle est ta ville principale de recherche ? *(ex: Montréal, Toronto, New York, Paris)*",
    "Dernière étape ! **Question 5/5 :** Possèdes-tu déjà une autorisation de travail aux États-Unis (citoyenneté US, Green Card, visa éligible sans parrainage) ? *(oui / non)*",
]

MONTHS_FR: Dict[str, int] = {
    "janvier": 1, "jan": 1,
    "fevrier": 2, "février": 2, "fev": 2, "fév": 2,
    "mars": 3, "mar": 3,
    "avril": 4, "avr": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7, "juil": 7,
    "aout": 8, "août": 8,
    "septembre": 9, "sep": 9, "sept": 9,
    "octobre": 10, "oct": 10,
    "novembre": 11, "nov": 11,
    "decembre": 12, "décembre": 12, "dec": 12, "déc": 12,
}


def parse_year(text: str) -> int | None:
    """Extrait l'année d'études (1 à 5)."""
    cleaned = text.strip().lower()
    match = re.search(r"\b([1-5])\b", cleaned)
    if match:
        return int(match.group(1))
    if "premi" in cleaned or "1re" in cleaned or "1ere" in cleaned or "1er" in cleaned:
        return 1
    if "deuxi" in cleaned or "2e" in cleaned or "2eme" in cleaned:
        return 2
    if "troisi" in cleaned or "3e" in cleaned:
        return 3
    if "quatri" in cleaned or "4e" in cleaned:
        return 4
    return None


def parse_graduation(text: str) -> str | None:
    """Extrait et normalise une date de diplomation au format YYYY-MM-15."""
    cleaned = text.strip().lower()
    # Format YYYY-MM ou YYYY/MM
    m_iso = re.search(r"\b(202[5-9]|203[0-5])[-/\s](0?[1-9]|1[0-2])\b", cleaned)
    if m_iso:
        year = int(m_iso.group(1))
        month = int(m_iso.group(2))
        return f"{year:04d}-{month:02d}-15"

    # Format MM/YYYY ou MM-YYYY
    m_rev = re.search(r"\b(0?[1-9]|1[0-2])[-/\s](202[5-9]|203[0-5])\b", cleaned)
    if m_rev:
        month = int(m_rev.group(1))
        year = int(m_rev.group(2))
        return f"{year:04d}-{month:02d}-15"

    # Mois en français + année (ex: mai 2029)
    year_match = re.search(r"\b(202[5-9]|203[0-5])\b", cleaned)
    if year_match:
        year = int(year_match.group(1))
        for m_name, m_num in MONTHS_FR.items():
            if m_name in cleaned:
                return f"{year:04d}-{m_num:02d}-15"
        # Si seulement l'année est fournie, par défaut mai (fin de session d'hiver)
        return f"{year:04d}-05-15"

    return None


def parse_interests(text: str, allowed_tags: List[str] | None = None) -> List[str]:
    """Extrait les tags d'intérêts valides à partir d'une réponse texte."""
    tags = allowed_tags or AVAILABLE_INTERESTS
    cleaned = text.strip().lower()
    if any(w in cleaned for w in ("tous", "tout", "all", "n'importe")):
        return list(tags)

    aliases = {
        "ib": "investment_banking",
        "banque": "investment_banking",
        "m&a": "investment_banking",
        "marché": "markets",
        "marches": "markets",
        "trading": "markets",
        "am": "asset_management",
        "gestion": "asset_management",
        "vc": "venture_capital",
        "ia": "ai",
        "intelligence": "ai",
        "startup": "startups",
        "corporate": "corporate_finance",
        "credit": "corporate_finance",
        "crédit": "corporate_finance",
        "dev": "tech",
        "software": "tech",
        "software_engineering": "tech",
    }

    selected: List[str] = []
    for tag in tags:
        if tag in cleaned or tag.replace("_", " ") in cleaned:
            selected.append(tag)

    for alias, target in aliases.items():
        if re.search(rf"\b{re.escape(alias)}\b", cleaned) and target in tags and target not in selected:
            selected.append(target)

    return selected


def parse_cities(text: str) -> Tuple[str, List[str]]:
    """Extrait la ville principale (home_base) et la liste des villes mentionnées."""
    raw_parts = [p.strip() for p in re.split(r"[,;/]+", text) if p.strip()]
    if not raw_parts:
        return "Montréal", ["Montréal"]

    norm_map = {
        "montreal": "Montréal",
        "montréal": "Montréal",
        "mtl": "Montréal",
        "toronto": "Toronto",
        "new york": "New York",
        "nyc": "New York",
        "paris": "Paris",
        "londres": "London",
        "london": "London",
        "chicago": "Chicago",
        "vancouver": "Vancouver",
    }

    cities: List[str] = []
    for part in raw_parts:
        low = part.lower()
        mapped = norm_map.get(low, part.title())
        if mapped not in cities:
            cities.append(mapped)

    return cities[0], cities


def parse_us_auth(text: str) -> bool | None:
    """Interprète une réponse oui/non."""
    cleaned = text.strip().lower()
    if any(w in cleaned for w in ("oui", "yes", "ouais", "vrai", "true", "1", "j'ai")):
        return True
    if any(w in cleaned for w in ("non", "no", "nope", "faux", "false", "0", "pas")):
        return False
    return None


def process_onboarding_step(
    step: int,
    user_input: str,
    draft_answers: Dict[str, Any],
    allowed_tags: List[str] | None = None,
) -> Tuple[int, Dict[str, Any], str]:
    """
    Traite l'entrée utilisateur pour l'étape courante (0 à 4).
    Retourne (next_step, updated_answers, radar_reply).
    Lorsque next_step == 5, l'onboarding est terminé.
    """
    updated = dict(draft_answers)

    if step == 0:
        yr = parse_year(user_input)
        if yr is None:
            return 0, updated, "Je n'ai pas bien saisi l'année. Indique un chiffre entre **1** et **4** (ex: `1` pour 1re année)."
        updated["current_year"] = yr
        return 1, updated, QUESTIONS[1]

    if step == 1:
        grad = parse_graduation(user_input)
        if grad is None:
            return 1, updated, "Format de date non reconnu. Indique le mois et l'année prévus (ex: `2029-05` ou `Mai 2028`)."
        updated["graduation"] = grad
        return 2, updated, QUESTIONS[2]

    if step == 2:
        interests = parse_interests(user_input, allowed_tags)
        if not interests:
            return (
                2,
                updated,
                "Je n'ai reconnu aucun tag. Choisis au moins un domaine parmi : `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance` (ou tape `tous`).",
            )
        updated["interests"] = interests
        return 3, updated, QUESTIONS[3]

    if step == 3:
        home_base, cities = parse_cities(user_input)
        updated["home_base"] = home_base
        updated["target_cities"] = cities
        return 4, updated, QUESTIONS[4]

    if step == 4:
        us_auth = parse_us_auth(user_input)
        if us_auth is None:
            return 4, updated, "Réponds simplement par **oui** ou par **non**."
        updated["us_work_auth"] = us_auth
        summary = format_profile_summary(updated)
        return 5, updated, summary

    return 5, updated, format_profile_summary(updated)


def format_profile_summary(answers: Dict[str, Any]) -> str:
    """Génère le message de synthèse final de Radar."""
    yr = answers.get("current_year", 1)
    yr_str = "1re année" if yr == 1 else f"{yr}e année"
    grad = str(answers.get("graduation", "2029-05-15"))[:7]
    cities = ", ".join(answers.get("target_cities", [answers.get("home_base", "Montréal")]))
    interests = ", ".join(answers.get("interests", []))
    us_str = "Oui" if answers.get("us_work_auth", False) else "Non"

    return (
        f"🎯 **Voici ton profil :** {yr_str}, diplomation **{grad}**, "
        f"ville(s) ciblée(s) : **{cities}**, autorisation US : **{us_str}**.\n"
        f"**Intérêts retenus :** `{interests}`.\n\n"
        f"J'ai mis à jour le tableau de bord et calculé tes scores sur mesure juste en dessous !"
    )


def build_profile_from_answers(answers: Dict[str, Any], template_profile: Profile | None = None) -> Profile:
    """Construit une instance de `Profile` compatible avec `radar/models.py`."""
    grad_str = str(answers.get("graduation", "2029-05-15"))
    # Le modèle Profile attend une `date` : convertir systématiquement.
    grad_value: Any = grad_str
    try:
        parts = [int(x) for x in grad_str.split("-")]
        grad_value = date(parts[0], parts[1], parts[2] if len(parts) > 2 else 15)
    except Exception:
        if template_profile is not None:
            grad_value = getattr(template_profile, "graduation", grad_str)

    kwargs: Dict[str, Any] = {
        "name": "Visiteur Radar",
        "school": getattr(template_profile, "school", "Université"),
        "program": getattr(template_profile, "program", "Finance / Quant / Tech"),
        "current_year": int(answers.get("current_year", 1)),
        "graduation": grad_value,
        "us_work_auth": bool(answers.get("us_work_auth", False)),
        "languages": getattr(template_profile, "languages", ["fr", "en"]),
        "home_base": str(answers.get("home_base", "Montréal")),
        "open_to_remote": getattr(template_profile, "open_to_remote", True),
        "interests": list(answers.get("interests", ["quant", "markets"])),
    }

    # Filtrage dynamique sur les champs réels de la dataclass Profile
    if hasattr(Profile, "__dataclass_fields__"):
        valid_fields = set(Profile.__dataclass_fields__.keys())
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return Profile(**filtered_kwargs)

    return Profile(**kwargs)