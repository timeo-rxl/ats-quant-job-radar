"""ats-quant-job-radar — internship radar for early-career students
in finance, quant and tech. Curated data, no scraping."""

from .data import load_profile, load_programs
from .matching import eligibility, filter_programs, match_score, rank_for_profile
from .models import InternshipProgram, Profile
from .timeline import STATUS_FR, days_until, deadline_status, upcoming

__all__ = [
    "Profile",
    "InternshipProgram",
    "load_programs",
    "load_profile",
    "eligibility",
    "match_score",
    "filter_programs",
    "rank_for_profile",
    "deadline_status",
    "days_until",
    "upcoming",
    "STATUS_FR",
]
