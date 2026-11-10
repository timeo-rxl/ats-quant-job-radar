"""Deadlines: what is open, what is closing, what is gone.

Deadlines move every year and this dataset is a snapshot, so every
status is computed from a ``today`` you can set — the demo uses the
real date, the tests use a fixed one.
"""

from __future__ import annotations

from datetime import date

from .models import InternshipProgram

URGENT_DAYS = 14


def deadline_status(program: InternshipProgram, today: date) -> str:
    """open | urgent | closed | watch."""
    if program.deadline is None:
        return "watch"
    if today > program.deadline:
        return "closed"
    if (program.deadline - today).days <= URGENT_DAYS:
        return "urgent"
    return "open"


def days_until(program: InternshipProgram, today: date) -> int | None:
    if program.deadline is None:
        return None
    return (program.deadline - today).days


def upcoming(
    programs: list[InternshipProgram], today: date
) -> list[tuple[InternshipProgram, str]]:
    """Dated deadlines first (soonest first), then watch-list items."""
    dated = [(p, deadline_status(p, today)) for p in programs if p.deadline]
    dated.sort(key=lambda ps: ps[0].deadline or date.max)
    watching = [(p, "watch") for p in programs if p.deadline is None]
    return dated + watching


STATUS_FR = {
    "open": "ouvert",
    "urgent": "ferme bientôt",
    "closed": "fermé",
    "watch": "à surveiller",
}
