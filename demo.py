"""Demo: ton radar, pour ton profil.

Usage:
    python demo.py                        # profil my_profile.yaml, date du jour
    python demo.py --profile my_profile.yaml --date 2027-01-15
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from radar import (  # noqa: E402
    STATUS_FR,
    days_until,
    deadline_status,
    eligibility,
    load_profile,
    load_programs,
    rank_for_profile,
    upcoming,
)


def _badge(p, today) -> str:
    status = deadline_status(p, today)
    if status == "closed":
        return "fermé"
    if status == "urgent":
        return f"ferme dans {days_until(p, today)} j"
    if status == "open":
        return f"ouvert ({days_until(p, today)} j)"
    return "à surveiller"


def main() -> None:
    parser = argparse.ArgumentParser(description="ATS quant job radar")
    parser.add_argument("--profile", default="my_profile.yaml")
    parser.add_argument("--date", default=None, help="AAAA-MM-JJ (défaut : aujourd'hui)")
    args = parser.parse_args()

    today = date.fromisoformat(args.date) if args.date else date.today()
    profile = load_profile(args.profile)
    programs = load_programs("data/programs.yaml")

    print(f"Radar stages — {profile.name} ({profile.school}, {profile.program})")
    print(f"Année : {profile.current_year}re  |  Diplomation : {profile.graduation_ym}  |  Aujourd'hui : {today}")
    print("=" * 72)

    ranked = rank_for_profile(programs, profile)
    print(f"\n✅ Pour toi ({len(ranked)} programmes) — meilleurs scores d'abord :")
    for p, score in ranked[:12]:
        verified = "✓ vérifié" if p.verified else "⚠️ à vérifier"
        print(f"  [{score:>3}] {p.label} — {_badge(p, today)} — {verified}")
        print(f"        {', '.join(p.locations)} | {p.type} | {p.deadline_note or ''}")
        if p.apply_url:
            print(f"        Postuler : {p.apply_url}")
        elif p.search_hint:
            print(f"        Chercher sur le site officiel : {p.search_hint}")

    print("\n❌ Pas pour toi maintenant — et pourquoi :")
    for p in programs:
        ok, reasons = eligibility(profile, p)
        if not ok:
            print(f"  · {p.label} : {'; '.join(reasons)}")

    print("\n⏰ Prochaines échéances :")
    for p, status in upcoming(programs, today)[:10]:
        if status == "watch":
            print(f"  · {p.label} — {STATUS_FR[status]} ({p.deadline_note})")
        else:
            print(f"  · {p.deadline} — {p.label} — {STATUS_FR[status]}")

    unverified = [p for p in programs if not p.verified]
    print(f"\nDonnées : {len(programs)} programmes, {len(programs) - len(unverified)} vérifiés, "
          f"{len(unverified)} à vérifier sur la page officielle avant de postuler.")
    print("Aucun scraping : les liens renvoient vers les pages officielles.")


if __name__ == "__main__":
    main()
