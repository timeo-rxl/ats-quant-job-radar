"""Load the dataset and the student's profile from YAML."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from .models import InternshipProgram, Profile


def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def load_programs(path: str | Path) -> list[InternshipProgram]:
    data = yaml.safe_load(Path(path).read_text())
    programs = []
    for item in data["programs"]:
        item = dict(item)
        item["deadline"] = _parse_date(item.get("deadline"))
        programs.append(InternshipProgram(**item))
    return programs


def load_profile(path: str | Path) -> Profile:
    data = yaml.safe_load(Path(path).read_text())
    data = dict(data)
    data["graduation"] = _parse_date(data["graduation"])
    return Profile(**data)
