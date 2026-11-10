# radar/i18n.py
"""Internationalisation (FR / EN) 100 % locale sans dépendance externe."""

from __future__ import annotations
import re
from typing import Dict

SUPPORTED_LANGS = ("fr", "en")
DEFAULT_LANG = "fr"

STRINGS: Dict[str, Dict[str, str]] = {
    # Sélecteur de langue
    "lang_selector_label": {
        "fr": "🌐 Langue / Language",
        "en": "🌐 Language / Langue",
    },
    # Hero Banner
    "hero_tag": {
        "fr": "Radar v2.1 • Finance, Quant & Tech",
        "en": "Radar v2.1 • Finance, Quant & Tech",
    },
    "hero_title": {
        "fr": "🎯 ATS Quant Job Radar",
        "en": "🎯 ATS Quant Job Radar",
    },
    "hero_subtitle": {
        "fr": "Identifie instantanément les programmes de stages auxquels tu es réellement admissible selon ton année d'études, ta date de diplomation et ton statut de visa.",
        "en": "Instantly find the internship programs you actually qualify for based on your study year, graduation date, and US work authorization.",
    },
    "btn_find_internships": {
        "fr": "🎯 Trouver mes stages (Assistant Radar)",
        "en": "🎯 Find my internships (Radar Assistant)",
    },
    "btn_reset_profile": {
        "fr": "🔄 Revenir au profil d'exemple",
        "en": "🔄 Reset to sample profile",
    },
    "btn_edit_profile": {
        "fr": "✏️ Modifier mon profil",
        "en": "✏️ Edit my profile",
    },
    "active_profile_banner": {
        "fr": "**Profil actif :** {name} • {year_label} • Diplomation `{grad}` • Base : **{city}** • Autorisation US : **{us}**",
        "en": "**Active profile:** {name} • {year_label} • Graduation `{grad}` • Home base: **{city}** • US Work Auth: **{us}**",
    },
    "yes": {"fr": "Oui", "en": "Yes"},
    "no": {"fr": "Non", "en": "No"},
    # Onboarding
    "onboarding_title": {
        "fr": "🎯 Onboarding interactif avec Radar",
        "en": "🎯 Interactive Onboarding with Radar",
    },
    "onboarding_caption": {
        "fr": "Réponds aux 5 questions une par une dans le chat ci-dessous (100 % local, sans clé API).",
        "en": "Answer the 5 quick questions one by one in the chat below (100% rule-based, no API key).",
    },
    "onboarding_tags_hint": {
        "fr": "💡 Tags disponibles : ",
        "en": "💡 Available tags: ",
    },
    "chat_input_placeholder": {
        "fr": "Écris ta réponse ici...",
        "en": "Type your answer here...",
    },
    "btn_see_results": {
        "fr": "✅ Voir mes résultats personnalisés",
        "en": "✅ View my personalized matches",
    },
    "btn_restart_onboarding": {
        "fr": "🔁 Recommencer les 5 questions",
        "en": "🔁 Restart the 5 questions",
    },
    # KPI Dashboard
    "kpi_eligible_label": {
        "fr": "Programmes admissibles",
        "en": "Eligible Programs",
    },
    "kpi_eligible_sub": {
        "fr": "Selon ton année, diplomation & visa",
        "en": "Based on your year, graduation & visa",
    },
    "kpi_deadlines_label": {
        "fr": "Deadlines ≤ 30 jours",
        "en": "Deadlines ≤ 30 days",
    },
    "kpi_deadlines_sub": {
        "fr": "Programmes ouverts à candidater",
        "en": "Open programs closing soon",
    },
    "kpi_next_label": {
        "fr": "Prochaine deadline",
        "en": "Next Deadline",
    },
    "kpi_next_none": {
        "fr": "Aucune fixe",
        "en": "No fixed date",
    },
    "kpi_next_days": {
        "fr": "J-{days}",
        "en": "{days}d left",
    },
    "kpi_next_sub": {
        "fr": "Compte à rebours prioritaire",
        "en": "Top priority countdown",
    },
    "kpi_montreal_label": {
        "fr": "Bureaux à Montréal",
        "en": "Montréal Offices",
    },
    "kpi_montreal_sub": {
        "fr": "Opportunités locales recensées",
        "en": "Local opportunities tracked",
    },
    # Urgent Banner
    "urgent_prefix": {
        "fr": "⚡ Prochaine échéance :",
        "en": "⚡ Next upcoming deadline:",
    },
    "urgent_deadline_info": {
        "fr": "(Date limite : <code>{deadline}</code>, dans <strong>{days} jour(s)</strong>)",
        "en": "(Deadline: <code>{deadline}</code>, in <strong>{days} day(s)</strong>)",
    },
    "urgent_cta": {
        "fr": "Postuler sur le site officiel ↗",
        "en": "Apply on official portal ↗",
    },
    # Charts
    "charts_expander": {
        "fr": "📊 Voir la répartition du marché (Catégories & Statuts des deadlines)",
        "en": "📊 Market Breakdown (Categories & Deadline Statuses)",
    },
    "chart_by_category": {
        "fr": "**Programmes par catégorie**",
        "en": "**Programs by Category**",
    },
    "chart_by_status": {
        "fr": "**Programmes par statut de deadline**",
        "en": "**Programs by Deadline Status**",
    },
    "status_open_chart": {"fr": "Ouvert", "en": "Open"},
    "status_urgent_chart": {"fr": "Ferme bientôt (≤14j)", "en": "Closing soon (≤14d)"},
    "status_watch_chart": {"fr": "À surveiller", "en": "To watch"},
    "status_closed_chart": {"fr": "Fermé", "en": "Closed"},
    # Honesty Box
    "honesty_box_html": {
        "fr": (
            "<strong>🛡️ Transparence des données :</strong> Ce radar repose sur un dataset curé manuellement "
            "({total} programmes, aucun scraping). <strong>{verified}</strong> programme(s) sont confirmés pour le cycle "
            "en cours et <strong>{unverified}</strong> sont étiquetés <em>« à vérifier sur la page officielle »</em>. "
            "Vérifie toujours les dates sur le portail de l'employeur."
        ),
        "en": (
            "<strong>🛡️ Data Transparency:</strong> This radar relies on a manually curated dataset "
            "({total} programs, zero scraping). <strong>{verified}</strong> program(s) are verified for the current cycle "
            "and <strong>{unverified}</strong> are labeled <em>\"to verify on official page\"</em>. "
            "Always double-check dates on the employer's career portal."
        ),
    },
    # Sidebar Filters
    "sidebar_header": {
        "fr": "🔎 Filtres de recherche",
        "en": "🔎 Search Filters",
    },
    "filter_search": {
        "fr": "Recherche (entreprise, mot-clé)",
        "en": "Search (firm, keyword)",
    },
    "filter_session": {
        "fr": "Session",
        "en": "Term / Session",
    },
    "filter_category": {
        "fr": "Catégorie",
        "en": "Category",
    },
    "filter_location": {
        "fr": "Lieu",
        "en": "Location",
    },
    "filter_all_f": {"fr": "Toutes", "en": "All"},
    "filter_all_m": {"fr": "Tous", "en": "All"},
    "filter_only_paid": {
        "fr": "Rémunéré uniquement",
        "en": "Paid only",
    },
    "filter_only_eligible": {
        "fr": "Admissible uniquement",
        "en": "Eligible only",
    },
    "filter_only_first_year": {
        "fr": "Ouvert aux 1re année (min_year ≤ 1)",
        "en": "Open to 1st-years / Freshmen (min_year ≤ 1)",
    },
    # Tabs
    "tab_programs": {
        "fr": "🎯 Programmes & Scores ({count})",
        "en": "🎯 Programs & Scores ({count})",
    },
    "tab_blockers": {
        "fr": "🚧 Ce qui te bloque (Plan d'action)",
        "en": "🚧 What's blocking you (Action Plan)",
    },
    "tab_tracker": {
        "fr": "📋 Suivi de candidatures ({count})",
        "en": "📋 Application Tracker ({count})",
    },
    # Badges
    "badge_urgent_days": {"fr": "🔥 Ferme bientôt ({days} j)", "en": "🔥 Closing soon ({days}d)"},
    "badge_urgent": {"fr": "🔥 Ferme bientôt", "en": "🔥 Closing soon"},
    "badge_open_days": {"fr": "✅ Ouvert ({days} j)", "en": "✅ Open ({days}d)"},
    "badge_open": {"fr": "✅ Ouvert", "en": "✅ Open"},
    "badge_closed": {"fr": "🔒 Fermé", "en": "🔒 Closed"},
    "badge_watch": {"fr": "👀 À surveiller", "en": "👀 To watch"},
    "badge_verified": {"fr": "✓ Vérifié", "en": "✓ Verified"},
    "badge_unverified": {
        "fr": "⚠️ À vérifier sur la page officielle",
        "en": "⚠️ Verify on official page",
    },
    # Program List & Score Breakdown
    "no_programs_match": {
        "fr": "Aucun programme ne correspond aux filtres sélectionnés.",
        "en": "No programs match the selected filters.",
    },
    "expander_program_details": {
        "fr": "Détails du score, admissibilité & suivi — {firm} ({title})",
        "en": "Score breakdown, eligibility & tracking — {firm} ({title})",
    },
    "eligible_header": {
        "fr": "#### ✅ Admissible — Décomposition du score",
        "en": "#### ✅ Eligible — Score Breakdown",
    },
    "score_base_line": {
        "fr": "- **Admissibilité validée :** `+{pts} pts`",
        "en": "- **Eligibility verified:** `+{pts} pts`",
    },
    "score_interests_line": {
        "fr": "- **Intérêts partagés ({count}) :** `+{pts} pts` {tags}",
        "en": "- **Shared interests ({count}):** `+{pts} pts` {tags}",
    },
    "no_shared_tags": {
        "fr": "(aucun tag commun)",
        "en": "(no shared tags)",
    },
    "score_location_line": {
        "fr": "- **Ville cible ({city}) :** `+{pts} pts`",
        "en": "- **Target city ({city}):** `+{pts} pts`",
    },
    "score_paid_line": {
        "fr": "- **Stage rémunéré :** `+{pts} pts`",
        "en": "- **Paid internship:** `+{pts} pts`",
    },
    "score_total_line": {
        "fr": "- **Total :** **{total} / 100**",
        "en": "- **Total:** **{total} / 100**",
    },
    "ineligible_header": {
        "fr": "#### ❌ Non admissible (Score : 0 / 100)",
        "en": "#### ❌ Not Eligible (Score: 0 / 100)",
    },
    "recommended_action_label": {
        "fr": "💡 **Action recommandée :** {hint}",
        "en": "💡 **Recommended action:** {hint}",
    },
    "deadline_label": {
        "fr": "**Date limite :** `{dl}` {note}",
        "en": "**Deadline:** `{dl}` {note}",
    },
    "deadline_unspecified": {
        "fr": "Non spécifiée",
        "en": "Not specified",
    },
    "note_prefix": {
        "fr": "Note : {notes}",
        "en": "Note: {notes}",
    },
    "btn_official_apply": {
        "fr": "🌐 Ouvrir la page officielle de candidature",
        "en": "🌐 Open official application page",
    },
    # Tracker inside card
    "track_section_header": {
        "fr": "#### 📌 Suivre cette candidature",
        "en": "#### 📌 Track this application",
    },
    "track_status_label": {
        "fr": "Statut",
        "en": "Status",
    },
    "track_note_label": {
        "fr": "Note personnelle",
        "en": "Personal note",
    },
    "track_note_placeholder": {
        "fr": "Ex: Référé par un alumnus, CV envoyé...",
        "en": "E.g., Referred by alumnus, resume submitted...",
    },
    "btn_save_tracking": {
        "fr": "💾 Enregistrer le suivi",
        "en": "💾 Save tracking",
    },
    "msg_tracking_saved": {
        "fr": "Suivi mis à jour dans SQLite !",
        "en": "Application status saved to SQLite!",
    },
    # Tab 2: Blockers
    "blockers_header": {
        "fr": "🚧 Programmes actuellement inaccessibles — et comment les débloquer",
        "en": "🚧 Currently Ineligible Programs — & How to Unlock Them",
    },
    "blockers_caption": {
        "fr": "Un « non » aujourd'hui prépare ta stratégie de l'an prochain. Voici pourquoi ces programmes te bloquent et l'action concrète associée.",
        "en": "A \"no\" today builds your recruiting strategy for next cycle. Here is why each program blocks you and what to target next.",
    },
    "blockers_none": {
        "fr": "🎉 Félicitations ! Tu es admissible à l'intégralité des programmes du radar.",
        "en": "🎉 Congratulations! You qualify for every single program in the radar.",
    },
    "blocker_reason_prefix": {
        "fr": "🔴 **Raison(s) du blocage :** {reasons}",
        "en": "🔴 **Blocking reason(s):** {reasons}",
    },
    "blocker_action_prefix": {
        "fr": "🎯 **Action concrète :**\n\n`{hint}`",
        "en": "🎯 **Next step:**\n\n`{hint}`",
    },
    # Tab 3: Tracker
    "tracker_tab_header": {
        "fr": "📋 Mes candidatures suivies (Base SQLite locale)",
        "en": "📋 My Tracked Applications (Local SQLite DB)",
    },
    "tracker_tab_caption": {
        "fr": "Les statuts sont sauvegardés localement via `sqlite3` sans jamais modifier `data/programs.yaml`.",
        "en": "Statuses are persisted locally via `sqlite3` without ever modifying `data/programs.yaml`.",
    },
    "btn_export_csv": {
        "fr": "📥 Exporter en CSV",
        "en": "📥 Export to CSV",
    },
    "tracker_empty_msg": {
        "fr": "Tu n'as encore suivi aucun programme. Ouvre les détails d'un programme dans le premier onglet pour lui attribuer un statut (À postuler, Postulé, Entretien, Offre, Refusé).",
        "en": "You haven't tracked any applications yet. Open a program's details in the first tab to set its status (To apply, Applied, Interview, Offer, Rejected).",
    },
    "col_firm": {"fr": "Entreprise", "en": "Firm"},
    "col_program": {"fr": "Programme", "en": "Program"},
    "col_status": {"fr": "Statut", "en": "Status"},
    "col_notes": {"fr": "Notes", "en": "Notes"},
    "col_updated": {"fr": "Mise à jour (UTC)", "en": "Updated (UTC)"},
}

# Correspondance canonique des statuts SQLite (stockés en français en base)
STATUS_FR_TO_EN: Dict[str, str] = {
    "Non suivi": "Not tracked",
    "À postuler": "To apply",
    "Postulé": "Applied",
    "Entretien": "Interview",
    "Offre": "Offer",
    "Refusé": "Rejected",
}
STATUS_EN_TO_FR: Dict[str, str] = {v: k for k, v in STATUS_FR_TO_EN.items()}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Retourne la chaîne traduite avec repli sur le français si la clé ou la langue manque."""
    lang_code = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
    entry = STRINGS.get(key, {})
    template = entry.get(lang_code) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def format_year_label(year: int, lang: str = DEFAULT_LANG) -> str:
    """Formate l'année d'études (ex: 1re année / 1st year)."""
    if lang == "en":
        suffixes = {1: "1st year", 2: "2nd year", 3: "3rd year", 4: "4th year"}
        return suffixes.get(year, f"Year {year}")
    return "1re année" if year == 1 else f"{year}e année"


def status_to_display(status_fr: str, lang: str = DEFAULT_LANG) -> str:
    """Traduit un statut SQLite canonique (FR) vers la langue d'affichage."""
    if lang == "en":
        return STATUS_FR_TO_EN.get(status_fr, status_fr)
    return status_fr


def status_from_input(status_any: str) -> str:
    """Normalise un statut (FR ou EN) vers la valeur canonique française stockée en SQLite."""
    if status_any in STATUS_EN_TO_FR:
        return STATUS_EN_TO_FR[status_any]
    return status_any


def translate_reason(reason_fr: str, lang: str = DEFAULT_LANG) -> str:
    """
    Traduit une raison d'inadmissibilité générée par `radar/matching.py` (en français)
    vers l'anglais sans modifier `radar/matching.py`.
    """
    if lang != "en" or not reason_fr:
        return reason_fr

    text = reason_fr.strip()

    # 1. Autorisation de travail US
    if any(k in text.lower() for k in ("autorisation", "états-unis", "etats-unis", "us work", "visa us")):
        return "Requires US work authorization without sponsorship"

    # 2. Année minimale — chaînes réelles de radar/matching.py :
    # "demande la 2e année minimum (profil : 1re année)" /
    # "réservé jusqu'à la 1e année (profil : 1re année)"
    m_min_yr = re.search(r"min(?:imum|imale)?[^\d]*(\d+)", text, flags=re.IGNORECASE)
    if not m_min_yr:
        m_min_yr = re.search(r"au moins[^\d]*(\d+)", text, flags=re.IGNORECASE)
    if not m_min_yr and ("année" in text.lower() and ("requiert" in text.lower() or " réservé" in text.lower())):
        m_min_yr = re.search(r"(\d+)(?:re|e|ère|eme)?\s*année", text, flags=re.IGNORECASE)

    if "année" in text.lower():
        nums = re.findall(r"\d+", text)
        low = text.lower()
        if ("max" in low or "plus" in low or "dépass" in low or "jusqu" in low) and nums:
            return f"Maximum study year is Year {nums[0]}"
        if nums:
            if len(nums) >= 2:
                return f"Requires at least Year {nums[0]} (current profile: Year {nums[1]})"
            return f"Requires at least Year {nums[0]}"

    # 3. Fenêtre de diplomation / grad_not_before / grad_window
    if any(k in text.lower() for k in ("diplomation", "diplôme", "graduation", "grad")):
        dates = re.findall(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", text)
        low = text.lower()
        if ("avant" in low or "antérieur" in low or "not_before" in low or "après" in low or "partir" in low) and len(dates) >= 1:
            if len(dates) >= 2:
                return f"Graduation must be on or after {dates[0]} (profile: {dates[1]})"
            return f"Graduation must be on or after {dates[0]}"
        if len(dates) >= 2:
            return f"Graduation window restricted to {dates[0]} – {dates[1]}"
        if len(dates) == 1:
            return f"Graduation date does not match target cohort ({dates[0]})"
        return "Graduation date outside target recruitment window"

    return text