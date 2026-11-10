"""Tests for the internship radar.

The reference date is fixed (10 Nov 2026) so deadline statuses are
deterministic. Expected eligibility comes from the Oct 2026 research
report: big-bank markets/IB roles need graduation Dec 2027 / 2028,
so a first-year graduating in 2029 is out; the realistic leads are
startups, fintech, VC and a few explicitly open bank roles.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from radar import (  # noqa: E402
    days_until,
    deadline_status,
    eligibility,
    filter_programs,
    load_profile,
    load_programs,
    match_score,
    rank_for_profile,
    upcoming,
)

TODAY = date(2026, 11, 10)


def load_all():
    return load_profile("my_profile.yaml"), load_programs("data/programs.yaml")


def by_id(programs, pid):
    return next(p for p in programs if p.id == pid)


class TestData(unittest.TestCase):
    def test_dataset_size(self):
        _, programs = load_all()
        self.assertEqual(len(programs), 31)

    def test_profile(self):
        profile, _ = load_all()
        self.assertEqual(profile.current_year, 1)
        self.assertEqual(profile.graduation, date(2029, 5, 15))
        self.assertFalse(profile.us_work_auth)


class TestEligibility(unittest.TestCase):
    def test_first_year_realistic_leads(self):
        profile, programs = load_all()
        for pid in ["bnc-corporate-finance", "bnp-corporate-credit",
                    "capital-one-strategy", "ea-ventures-finance",
                    "front-row-ventures", "bank-of-canada"]:
            ok, reasons = eligibility(profile, by_id(programs, pid))
            self.assertTrue(ok, f"{pid} should be eligible: {reasons}")

    def test_big_bank_markets_needs_later_graduation(self):
        profile, programs = load_all()
        for pid in ["rbc-global-markets", "td-ib", "bmo-summer-2027",
                    "goldman-summer-analyst"]:
            ok, reasons = eligibility(profile, by_id(programs, pid))
            self.assertFalse(ok, f"{pid} should reject a 2029 graduate")
            self.assertTrue(any("diplomation" in r for r in reasons), reasons)

    def test_us_work_auth_blocks(self):
        profile, programs = load_all()
        for pid in ["jpmorgan-emerging-talent", "janestreet-focus",
                    "kleiner-perkins-fellows"]:
            ok, reasons = eligibility(profile, by_id(programs, pid))
            self.assertFalse(ok, f"{pid} needs US work auth")
            self.assertTrue(any("États-Unis" in r for r in reasons), reasons)

    def test_sophomore_programmes_need_second_year(self):
        profile, programs = load_all()
        for pid in ["morgan-stanley-early-insights", "cpp-discover", "psp-stages"]:
            ok, _ = eligibility(profile, by_id(programs, pid))
            self.assertFalse(ok, f"{pid} needs year 2+")

    def test_eligible_count(self):
        profile, programs = load_all()
        eligible = [p for p in programs if eligibility(profile, p)[0]]
        self.assertEqual(len(eligible), 16)


class TestScoring(unittest.TestCase):
    def test_top_scores(self):
        profile, programs = load_all()
        ranked = rank_for_profile(programs, profile)
        top2 = {p.id for p, _ in ranked[:2]}
        self.assertEqual(top2, {"bnc-corporate-finance", "bnp-corporate-credit"})
        self.assertTrue(all(s == 100 for _, s in ranked[:2]))

    def test_ineligible_scores_zero(self):
        profile, programs = load_all()
        self.assertEqual(match_score(profile, by_id(programs, "rbc-global-markets")), 0)


class TestFilters(unittest.TestCase):
    def test_summer_2027_session(self):
        _, programs = load_all()
        self.assertEqual(len(filter_programs(programs, session="summer_2027")), 24)

    def test_first_year_only(self):
        _, programs = load_all()
        out = filter_programs(programs, first_year_only=True)
        self.assertEqual(len(out), 26)
        self.assertNotIn("psp-stages", [p.id for p in out])

    def test_query(self):
        _, programs = load_all()
        self.assertEqual(len(filter_programs(programs, query="citadel")), 1)
        self.assertEqual(len(filter_programs(programs, query="banque")), 3)

    def test_eligible_only(self):
        profile, programs = load_all()
        out = filter_programs(programs, profile=profile, eligible_only=True)
        self.assertEqual(len(out), 16)
        self.assertTrue(all(eligibility(profile, p)[0] for p in out))


class TestTimeline(unittest.TestCase):
    def test_closed_deadlines(self):
        _, programs = load_all()
        self.assertEqual(deadline_status(by_id(programs, "next36-2027"), TODAY), "closed")
        self.assertEqual(deadline_status(by_id(programs, "bmo-summer-2027"), TODAY), "closed")

    def test_open_deadline_days(self):
        _, programs = load_all()
        kp = by_id(programs, "kleiner-perkins-fellows")
        self.assertEqual(deadline_status(kp, TODAY), "open")
        self.assertEqual(days_until(kp, TODAY), 82)

    def test_watch_without_deadline(self):
        _, programs = load_all()
        self.assertEqual(deadline_status(by_id(programs, "bnp-corporate-credit"), TODAY), "watch")
        self.assertIsNone(days_until(by_id(programs, "bnp-corporate-credit"), TODAY))

    def test_upcoming_sorted(self):
        _, programs = load_all()
        up = upcoming(programs, TODAY)
        dated = [p for p, _ in up if p.deadline]
        self.assertEqual(dated, sorted(dated, key=lambda p: p.deadline))
        self.assertEqual(dated[0].id, "next36-2027")


if __name__ == "__main__":
    unittest.main()
