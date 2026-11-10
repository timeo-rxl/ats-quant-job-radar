# radar/onboarding.py
"""Moteur conversationnel bilingue (FR/EN) à base de règles pour l'assistant Radar (🎯)."""

from __future__ import annotations
import re
from datetime import date
from typing import Dict, Any, List, Tuple

from radar.models import Profile
from radar.i18n import format_year_label

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

INTEREST_LABELS_EN: Dict[str, str] = {
    "quant": "Quant & Quantitative Research",
    "markets": "Financial Markets (Sales & Trading)",
    "investment_banking": "Investment Banking (M&A / ECM / DCM)",
    "asset_management": "Asset & Portfolio Management",
    "fintech": "Fintech & Payments",
    "venture_capital": "Venture Capital (VC)",
    "ai": "Artificial Intelligence & Data",
    "startups": "Startups & Product",
    "corporate_finance": "Corporate Finance & Credit",
    "tech": "Tech & Software Engineering",
}

QUESTIONS_FR: List[str] = [
    "Salut ! Je suis **Radar** 🎯. En 5 questions rapides, je vais filtrer les programmes auxquels tu es *vraiment* admissible.\n\n**Question 1/5 :** En quelle année d'études universitaires es-tu actuellement ? *(ex: 1, 2, 3 ou 4)*",
    "Noté ! **Question 2/5 :** Quelle est ta date prévue de diplomation ? *(format AAAA-MM, ex: 2029-05 ou Mai 2029)*",
    "Parfait. **Question 3/5 :** Quels sont tes domaines d'intérêt ?\nTu peux écrire plusieurs mots-clés séparés par une virgule parmi : `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance`, `tech` *(ou tape « tous »)*.",
    "Bien reçu. **Question 4/5 :** Quelle est ta ville principale de recherche ? *(ex: Montréal, Toronto, New York, Paris)*",
    "Dernière étape ! **Question 5/5 :** Possèdes-tu déjà une autorisation de travail aux États-Unis (citoyenneté US, Green Card, visa éligible sans parrainage) ? *(oui / non)*",
]

QUESTIONS_EN: List[str] = [
    "Hi there! I'm **Radar** 🎯. In 5 quick questions, I'll filter the internship programs you *actually* qualify for.\n\n**Question 1/5:** What year of university are you currently in? *(e.g., 1, 2, 3, 4, freshman, sophomore)*",
    "Got it! **Question 2/5:** What is your expected graduation date? *(YYYY-MM format, e.g., 2029-05 or May 2029)*",
    "Awesome. **Question 3/5:** What are your main areas of interest?\nType one or more keywords separated by commas from: `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance`, `tech` *(or type \"all\")*.",
    "Noted. **Question 4/5:** What is your primary target city? *(e.g., Montréal, Toronto, New York, London, Paris)*",
    "Final step! **Question 5/5:** Do you already have US work authorization (US citizen, Green Card, or eligible visa without sponsorship)? *(yes / no)*",
]

# Rétrocompatibilité avec les imports existants `from radar.onboarding import QUESTIONS`
QUESTIONS: List[str] = QUESTIONS_FR


def get_questions(lang: str = "fr") -> List[str]:
    """Retourne la liste des 5 questions dans la langue demandée."""
    return QUESTIONS_EN if lang == "en" else QUESTIONS_FR


MONTHS_MAP: Dict[str, int] = {
    # Français
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
    # Anglais
    "january": 1,
    "february": 2, "feb": 2,
    "march": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_year(text: str) -> int | None:
    """Extrait l'année d'études (1 à 5) en français ou en anglais."""
    cleaned = text.strip().lower()
    # Chiffre explicite ou suivi de st/nd/rd/th/re/e
    match = re.search(r"\b([1-5])(?:st|nd|rd|th|re|ere|ère|e|eme|ème|er)?\b", cleaned)
    if match:
        return int(match.group(1))

    # Termes français & nord-américains (freshman, sophomore, junior, senior)
    if any(w in cleaned for w in ("premi", "freshman", "first year", "first-year", "u0", "u1")):
        return 1
    if any(w in cleaned for w in ("deuxi", "sophomore", "second year", "second-year", "u2")):
        return 2
    if any(w in cleaned for w in ("troisi", "junior", "third year", "third-year", "u3")):
        return 3
    if any(w in cleaned for w in ("quatri", "senior", "fourth year", "fourth-year", "u4")):
        return 4
    return None


def parse_graduation(text: str) -> str | None:
    """Extrait et normalise une date de diplomation au format YYYY-MM-15 (FR et EN)."""
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

    # Mois en français ou anglais + année (ex: mai 2029, May 2029, June 2028)
    year_match = re.search(r"\b(202[5-9]|203[0-5])\b", cleaned)
    if year_match:
        year = int(year_match.group(1))
        # Tri par longueur décroissante pour matcher "september" avant "sep"
        for m_name in sorted(MONTHS_MAP.keys(), key=len, reverse=True):
            if re.search(rf"\b{re.escape(m_name)}\b", cleaned):
                return f"{year:04d}-{MONTHS_MAP[m_name]:02d}-15"
        return f"{year:04d}-05-15"

    return None


def parse_interests(text: str, allowed_tags: List[str] | None = None) -> List[str]:
    """Extrait les tags d'intérêts valides à partir d'une réponse texte (FR ou EN)."""
    tags = allowed_tags or AVAILABLE_INTERESTS
    cleaned = text.strip().lower()
    if any(w in cleaned for w in ("tous", "tout", "all", "everything", "any", "n'importe")):
        return list(tags)

    aliases = {
        "ib": "investment_banking",
        "ibd": "investment_banking",
        "banque": "investment_banking",
        "banking": "investment_banking",
        "m&a": "investment_banking",
        "marché": "markets",
        "marches": "markets",
        "market": "markets",
        "trading": "markets",
        "sales": "markets",
        "am": "asset_management",
        "asset": "asset_management",
        "portfolio": "asset_management",
        "gestion": "asset_management",
        "vc": "venture_capital",
        "venture": "venture_capital",
        "ia": "ai",
        "ml": "ai",
        "data": "ai",
        "intelligence": "ai",
        "startup": "startups",
        "corporate": "corporate_finance",
        "credit": "corporate_finance",
        "crédit": "corporate_finance",
        "tech": "tech",
        "dev": "tech",
        "swe": "tech",
        "software": "tech",
        "software_engineering": "tech",
        "coding": "tech",
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
        "ny": "New York",
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
    """Interprète une réponse oui/non ou yes/no."""
    cleaned = text.strip().lower()
    if any(re.search(rf"\b{w}\b", cleaned) for w in ("oui", "yes", "yep", "yeah", "ouais", "vrai", "true", "1", "authorized")):
        return True
    if any(re.search(rf"\b{w}\b", cleaned) for w in ("non", "no", "nope", "nah", "faux", "false", "0", "pas")):
        return False
    return None


def process_onboarding_step(
    step: int,
    user_input: str,
    draft_answers: Dict[str, Any],
    allowed_tags: List[str] | None = None,
    lang: str = "fr",
) -> Tuple[int, Dict[str, Any], str]:
    """
    Traite l'entrée utilisateur pour l'étape courante (0 à 4) en FR ou EN.
    Retourne (next_step, updated_answers, radar_reply).
    """
    updated = dict(draft_answers)
    questions = get_questions(lang)
    is_en = lang == "en"

    if step == 0:
        yr = parse_year(user_input)
        if yr is None:
            err = (
                "I didn't catch your study year. Please enter a number between **1** and **4** (e.g., `1` or `freshman`)."
                if is_en
                else "Je n'ai pas bien saisi l'année. Indique un chiffre entre **1** et **4** (ex: `1` pour 1re année)."
            )
            return 0, updated, err
        updated["current_year"] = yr
        return 1, updated, questions[1]

    if step == 1:
        grad = parse_graduation(user_input)
        if grad is None:
            err = (
                "Unrecognized date format. Please enter your expected graduation month and year (e.g., `2029-05` or `May 2029`)."
                if is_en
                else "Format de date non reconnu. Indique le mois et l'année prévus (ex: `2029-05` ou `Mai 2028`)."
            )
            return 1, updated, err
        updated["graduation"] = grad
        return 2, updated, questions[2]

    if step == 2:
        interests = parse_interests(user_input, allowed_tags)
        if not interests:
            err = (
                "I didn't recognize any interest tag. Pick at least one from: `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance`, `tech` (or type `all`)."
                if is_en
                else "Je n'ai reconnu aucun tag. Choisis au moins un domaine parmi : `quant`, `markets`, `investment_banking`, `asset_management`, `fintech`, `venture_capital`, `ai`, `startups`, `corporate_finance`, `tech` (ou tape `tous`)."
            )
            return 2, updated, err
        updated["interests"] = interests
        return 3, updated, questions[3]

    if step == 3:
        home_base, cities = parse_cities(user_input)
        updated["home_base"] = home_base
        updated["target_cities"] = cities
        return 4, updated, questions[4]

    if step == 4:
        us_auth = parse_us_auth(user_input)
        if us_auth is None:
            err = (
                "Please reply with **yes** or **no**."
                if is_en
                else "Réponds simplement par **oui** ou par **non**."
            )
            return 4, updated, err
        updated["us_work_auth"] = us_auth
        summary = format_profile_summary(updated, lang=lang)
        return 5, updated, summary

    return 5, updated, format_profile_summary(updated, lang=lang)


def format_profile_summary(answers: Dict[str, Any], lang: str = "fr") -> str:
    """Génère le message de synthèse final de Radar en FR ou EN."""
    yr = int(answers.get("current_year", 1))
    yr_str = format_year_label(yr, lang=lang)
    grad = str(answers.get("graduation", "2029-05-15"))[:7]
    cities = ", ".join(answers.get("target_cities", [answers.get("home_base", "Montréal")]))
    interests = ", ".join(answers.get("interests", []))

    if lang == "en":
        us_str = "Yes" if answers.get("us_work_auth", False) else "No"
        return (
            f"🎯 **Here is your profile:** {yr_str}, graduation **{grad}**, "
            f"target city/cities: **{cities}**, US work authorization: **{us_str}**.\n"
            f"**Selected interests:** `{interests}`.\n\n"
            f"I've updated the dashboard and ranked your personalized matches right below!"
        )

    us_str = "Oui" if answers.get("us_work_auth", False) else "Non"
    return (
        f"🎯 **Voici ton profil :** {yr_str}, diplomation **{grad}**, "
        f"ville(s) ciblée(s) : **{cities}**, autorisation US : **{us_str}**.\n"
        f"**Intérêts retenus :** `{interests}`.\n\n"
        f"J'ai mis à jour le tableau de bord et calculé tes scores sur mesure juste en dessous !"
    )


def build_profile_from_answers(
    answers: Dict[str, Any],
    template_profile: Profile | None = None,
    lang: str = "fr",
) -> Profile:
    """Construit une instance de `Profile` compatible avec `radar/models.py` (graduation en `date` ou `str`)."""
    grad_str = str(answers.get("graduation", "2029-05-15"))
    grad_value: Any = grad_str

    # Dans radar/data.py, `graduation` est typé `date` : on convertit par défaut en `date`
    # sauf si un template_profile utilise explicitement une `str` (ex: dans certains mocks de tests).
    should_be_date = True
    if template_profile is not None and isinstance(getattr(template_profile, "graduation", None), str):
        should_be_date = False

    if should_be_date:
        try:
            parts = [int(x) for x in grad_str.split("-")]
            grad_value = date(parts[0], parts[1], parts[2] if len(parts) > 2 else 15)
        except Exception:
            grad_value = getattr(template_profile, "graduation", grad_str)

    default_name = "Radar Visitor" if lang == "en" else "Visiteur Radar"

    kwargs: Dict[str, Any] = {
        "name": default_name,
        "school": getattr(template_profile, "school", "University" if lang == "en" else "Université"),
        "program": getattr(template_profile, "program", "Finance / Quant / Tech"),
        "current_year": int(answers.get("current_year", 1)),
        "graduation": grad_value,
        "us_work_auth": bool(answers.get("us_work_auth", False)),
        "languages": getattr(template_profile, "languages", ["fr", "en"]),
        "home_base": str(answers.get("home_base", "Montréal")),
        "open_to_remote": getattr(template_profile, "open_to_remote", True),
        "interests": list(answers.get("interests", ["quant", "markets"])),
    }

    if hasattr(Profile, "__dataclass_fields__"):
        valid_fields = set(Profile.__dataclass_fields__.keys())
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        return Profile(**filtered_kwargs)

    return Profile(**kwargs)