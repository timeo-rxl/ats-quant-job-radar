"""Data structures for the internship radar.

One idea: a programme is a fact sheet (who, when, where, who can
apply, when it closes), and a profile is one student. Everything the
matching needs lives in these two objects — no scraping, no hidden
state. Money and dates are explicit; anything unverified is labelled
as such in the data, never silently treated as fact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Profile:
    """One student, described the way recruiters describe eligibility."""

    name: str
    school: str
    program: str
    current_year: int                 # 1 = first year of undergrad
    graduation: date                  # expected graduation date
    us_work_auth: bool = False
    languages: list[str] = field(default_factory=lambda: ["fr", "en"])
    home_base: str = "Montréal"
    open_to_remote: bool = True
    interests: list[str] = field(default_factory=list)
    # interest tags: quant, markets, investment_banking, asset_management,
    # fintech, venture_capital, ai, startups, corporate_finance, tech

    @property
    def graduation_ym(self) -> str:
        return self.graduation.strftime("%Y-%m")


@dataclass
class InternshipProgram:
    """One internship / fellowship / student programme."""

    id: str
    firm: str
    program: str
    type: str                         # internship | fellowship | program |
    # vc_associate | accelerator | insight
    category: str                     # banking | quant | tech | vc_startup | public
    locations: list[str] = field(default_factory=list)
    remote: bool | None = None        # None = unknown
    sessions: list[str] = field(default_factory=list)
    # e.g. summer_2027, winter_2027, fall_2027, school_year, summer_2028
    paid: bool | None = None          # None = unknown
    min_year: int | None = None       # first year of study eligible (None = any)
    max_year: int | None = None
    grad_not_before: str | None = None   # "YYYY-MM": graduate on/after this
    grad_window: list[str] | None = None  # ["YYYY-MM", "YYYY-MM"]: graduate inside
    requires_us_auth: bool = False
    interests: list[str] = field(default_factory=list)
    deadline: date | None = None
    deadline_note: str = ""
    apply_url: str | None = None
    source: str = ""
    verified: bool = False            # True = checked against the source
    verified_date: str = ""
    search_hint: str = ""             # what to search on the official site
    notes: str = ""

    @property
    def label(self) -> str:
        return f"{self.firm} — {self.program}"
