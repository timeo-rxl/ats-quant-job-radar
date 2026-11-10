# radar/scoring.py
"""Décomposition du score, recommandations d'action et calcul des KPI."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any, List, Dict, Tuple

from radar.matching import eligibility, match_score
from radar.timeline import deadline_status, days_until


@dataclass
class ScoreBreakdown:
    total: int
    eligible: bool
    base_points: int
    interest_points: int
    location_points: int
    paid_points: int
    shared_interests: List[str]
    reasons: List[str]
    action_hint: str


def _unpack_eligibility(elig_result: Any) -> Tuple[bool, List[str]]:
    """Adaptateur sécurisé pour lire le retour de eligibility() quel que soit son format exact."""
    if isinstance(elig_result, tuple) and len(elig_result) == 2:
        first, second = elig_result
        if isinstance(first, bool):
            return first, list(second) if second else []
    if hasattr(elig_result, "eligible"):
        reasons = getattr(elig_result, "reasons", [])
        return bool(elig_result.eligible), list(reasons)
    if isinstance(elig_result, dict):
        return bool(elig_result.get("eligible", False)), list(elig_result.get("reasons", []))
    if isinstance(elig_result, list):
        return len(elig_result) == 0, elig_result
    return bool(elig_result), []


def build_action_hint(reasons: List[str], program: Any) -> str:
    """Traduit les raisons de refus en une action concrète pour le candidat."""
    if not reasons:
        return "Admissible dès maintenant — prépare ton CV."

    hints = []
    joined = " ".join(reasons).lower()

    min_yr = getattr(program, "min_year", None)
    max_yr = getattr(program, "max_year", None)
    grad_win = getattr(program, "grad_window", None)
    grad_nb = getattr(program, "grad_not_before", None)

    if getattr(program, "requires_us_auth", False) and (
        "us" in joined or "états-unis" in joined or "autorisation" in joined or "visa" in joined
    ):
        hints.append("Il te faudra une autorisation de travail US (ou cibler les bureaux canadiens/européens)")

    if "année" in joined or "year" in joined:
        if min_yr and min_yr > 1:
            hints.append(f"Re-postule en {min_yr}e année")
        elif max_yr:
            hints.append(f"Réservé aux étudiants de {max_yr}e année max")

    if "diplomation" in joined or "grad" in joined or "diplôme" in joined:
        if grad_win:
            if isinstance(grad_win, (list, tuple)) and len(grad_win) >= 2:
                hints.append(f"Diplomations {grad_win[0]}–{grad_win[-1]} seulement")
            else:
                hints.append(f"Fenêtre de diplomation : {grad_win}")
        elif grad_nb:
            hints.append(f"Diplomation requise après {grad_nb}")
        else:
            hints.append("Vise ce programme lorsque ta date de diplomation entrera dans la fenêtre cible")

    if not hints:
        return "Vérifie l'évolution des critères d'admissibilité lors de la prochaine saison de recrutement"

    return " • ".join(hints)


def explain_score(profile: Any, program: Any) -> ScoreBreakdown:
    """Calcule et décompose le score d'un programme pour un profil donné."""
    raw_elig = eligibility(profile, program)
    is_elig, reasons = _unpack_eligibility(raw_elig)

    if not is_elig:
        return ScoreBreakdown(
            total=0,
            eligible=False,
            base_points=0,
            interest_points=0,
            location_points=0,
            paid_points=0,
            shared_interests=[],
            reasons=reasons,
            action_hint=build_action_hint(reasons, program),
        )

    base_pts = 50

    # Intérêts partagés (jusqu'à 30 pts)
    prof_interests = set(getattr(profile, "interests", []) or [])
    prog_interests = list(getattr(program, "interests", []) or [])
    shared = [i for i in prog_interests if i in prof_interests]

    # Déduction exacte pour s'aligner à 100 % sur match_score() existant
    official_total = int(match_score(profile, program))

    # Ville d'origine (+10 pts) — même règle exacte que match_score() :
    # la ville du profil doit figurer telle quelle dans les lieux du programme.
    home_base = (getattr(profile, "home_base", "") or "").strip().lower()
    locations = [str(loc).strip().lower() for loc in (getattr(program, "locations", []) or [])]
    loc_pts = 10 if home_base and home_base in locations else 0

    # Rémunéré (+10 pts)
    paid_pts = 10 if getattr(program, "paid", False) else 0

    # Calcul des points d'intérêts cohérent avec le score officiel
    interest_pts = max(0, min(30, official_total - base_pts - loc_pts - paid_pts))

    return ScoreBreakdown(
        total=official_total,
        eligible=True,
        base_points=base_pts,
        interest_points=interest_pts,
        location_points=loc_pts,
        paid_points=paid_pts,
        shared_interests=shared,
        reasons=[],
        action_hint="Admissible — prêt à postuler",
    )


def _safe_deadline_status(program: Any, today: date | None = None) -> str:
    """Statut de deadline via la signature réelle : deadline_status(program, today)."""
    today = today or date.today()
    return str(deadline_status(program, today))


def _safe_days_until(program: Any, today: date | None = None) -> int | None:
    """Jours restants via la signature réelle : days_until(program, today)."""
    today = today or date.today()
    if getattr(program, "deadline", None) is None:
        return None
    return days_until(program, today)


def compute_kpis(profile: Any, programs: List[Any], today: date | None = None) -> Dict[str, Any]:
    """Calcule toutes les métriques du tableau de bord KPI."""
    today = today or date.today()
    total_count = len(programs)
    eligible_count = 0
    deadlines_30d = 0
    montreal_count = 0

    next_deadline_days: int | None = None
    most_urgent_program: Any | None = None

    by_category: Dict[str, int] = {}
    by_status: Dict[str, int] = {"open": 0, "urgent": 0, "watch": 0, "closed": 0}

    for prog in programs:
        bd = explain_score(profile, prog)
        if bd.eligible:
            eligible_count += 1

        # Compteur Montréal
        locs = [str(l).lower() for l in (getattr(prog, "locations", []) or [])]
        if any("montréal" in l or "montreal" in l for l in locs):
            montreal_count += 1

        # Catégories
        cat = str(getattr(prog, "category", "Autre") or "Autre")
        by_category[cat] = by_category.get(cat, 0) + 1

        # Statuts et échéances
        status = _safe_deadline_status(prog, today).lower()
        if status in by_status:
            by_status[status] += 1
        else:
            by_status[status] = 1

        d_left = _safe_days_until(prog, today)
        if d_left is not None and d_left >= 0 and status in ("open", "urgent"):
            if d_left <= 30:
                deadlines_30d += 1
            if next_deadline_days is None or d_left < next_deadline_days:
                next_deadline_days = d_left
                most_urgent_program = prog

    return {
        "eligible_count": eligible_count,
        "total_count": total_count,
        "deadlines_30d": deadlines_30d,
        "next_deadline_days": next_deadline_days,
        "most_urgent_program": most_urgent_program,
        "montreal_count": montreal_count,
        "by_category": by_category,
        "by_status": by_status,
    }