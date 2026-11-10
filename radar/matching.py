"""Matching: is this programme for this student, and why (not)?

Eligibility is a checklist, not a black box. Every rejection carries
its reason in plain language, so a "no" tells you what to aim for
next year instead of just closing a door.
"""

from __future__ import annotations

from .models import InternshipProgram, Profile


def eligibility(profile: Profile, program: InternshipProgram) -> tuple[bool, list[str]]:
    """(eligible, reasons). Reasons are in French, written for the student."""
    reasons: list[str] = []

    if program.min_year is not None and profile.current_year < program.min_year:
        reasons.append(
            f"demande la {program.min_year}e année minimum "
            f"(profil : {profile.current_year}re année)"
        )
    if program.max_year is not None and profile.current_year > program.max_year:
        reasons.append(
            f"réservé jusqu'à la {program.max_year}e année "
            f"(profil : {profile.current_year}re année)"
        )
    grad = profile.graduation_ym
    if program.grad_not_before is not None and grad < program.grad_not_before:
        reasons.append(
            f"demande une diplomation à partir de {program.grad_not_before} "
            f"(diplomation du profil : {grad})"
        )
    if program.grad_window is not None:
        start, end = program.grad_window
        if not (start <= grad <= end):
            reasons.append(
                f"demande une diplomation entre {start} et {end} "
                f"(diplomation du profil : {grad})"
            )
    if program.requires_us_auth and not profile.us_work_auth:
        reasons.append("exige une autorisation de travail aux États-Unis")
    return (not reasons, reasons)


def match_score(profile: Profile, program: InternshipProgram) -> int:
    """0–100, explainable. 0 if not eligible — a perfect score on a
    programme you cannot join is a lie.

    50 points for being eligible, up to 30 for shared interests,
    10 for Montréal (home base), 10 if paid.
    """
    eligible, _ = eligibility(profile, program)
    if not eligible:
        return 0
    score = 50
    if program.interests:
        overlap = len(set(profile.interests) & set(program.interests))
        score += round(30 * overlap / len(program.interests))
    if profile.home_base in program.locations:
        score += 10
    if program.paid:
        score += 10
    return min(score, 100)


def filter_programs(
    programs: list[InternshipProgram],
    profile: Profile | None = None,
    session: str | None = None,
    category: str | None = None,
    location: str | None = None,
    paid_only: bool = False,
    eligible_only: bool = False,
    first_year_only: bool = False,
    query: str | None = None,
) -> list[InternshipProgram]:
    """All filters combine (AND). No filter = everything."""
    out = []
    for p in programs:
        if session is not None and session not in p.sessions:
            continue
        if category is not None and p.category != category:
            continue
        if location is not None and location not in p.locations:
            continue
        if paid_only and p.paid is not True:
            continue
        if eligible_only and profile is not None:
            ok, _ = eligibility(profile, p)
            if not ok:
                continue
        if first_year_only:
            if p.min_year is not None and p.min_year > 1:
                continue
        if query:
            q = query.lower()
            hay = f"{p.firm} {p.program} {p.category} {' '.join(p.interests)}".lower()
            if q not in hay:
                continue
        out.append(p)
    return out


def rank_for_profile(
    programs: list[InternshipProgram], profile: Profile
) -> list[tuple[InternshipProgram, int]]:
    """Eligible programmes first, best score first. Ineligible ones
    are dropped here — see ``eligibility`` for the why."""
    ranked = [(p, match_score(profile, p)) for p in programs]
    ranked = [(p, s) for p, s in ranked if s > 0]
    ranked.sort(key=lambda ps: (-ps[1], ps[0].firm))
    return ranked
