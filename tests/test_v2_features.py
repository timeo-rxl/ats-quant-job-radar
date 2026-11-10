# tests/test_v2_features.py
"""Tests unitaires pour les nouveautés Radar v2.0 (scoring, onboarding, tracker SQLite)."""

from datetime import date
from pathlib import Path

import pytest

from radar.models import Profile, InternshipProgram
from radar.scoring import explain_score, compute_kpis, build_action_hint
from radar.onboarding import (
    parse_year,
    parse_graduation,
    parse_interests,
    parse_us_auth,
    process_onboarding_step,
    build_profile_from_answers,
)
from radar.tracker import (
    init_db,
    set_application_status,
    get_application,
    get_all_tracked,
    export_tracked_to_csv,
)


def _make_sample_profile(**overrides) -> Profile:
    defaults = dict(
        name="Test User",
        school="HEC Montréal",
        program="B.A.A.",
        current_year=1,
        graduation=date(2029, 5, 15),
        us_work_auth=False,
        languages=["fr", "en"],
        home_base="Montréal",
        open_to_remote=True,
        interests=["quant", "markets", "corporate_finance"],
    )
    defaults.update(overrides)
    if hasattr(Profile, "__dataclass_fields__"):
        valid = set(Profile.__dataclass_fields__.keys())
        defaults = {k: v for k, v in defaults.items() if k in valid}
    return Profile(**defaults)


def _make_sample_program(**overrides) -> InternshipProgram:
    defaults = dict(
        id="test-prog-1",
        firm="Banque Test",
        program="Analyste Crédit",
        type="summer_internship",
        category="corporate_finance",
        locations=["Montréal"],
        remote=False,
        sessions=["Été 2027"],
        paid=True,
        min_year=1,
        max_year=3,
        grad_not_before="2028-01",
        grad_window=None,
        requires_us_auth=False,
        interests=["corporate_finance", "markets"],
        deadline=date(2026, 11, 20),
        deadline_note="Rolling",
        apply_url="https://example.com",
        source="https://example.com",
        verified=True,
        verified_date="2026-10-01",
        search_hint="Banque Test stage",
        notes="Test note",
    )
    defaults.update(overrides)
    if hasattr(InternshipProgram, "__dataclass_fields__"):
        valid = set(InternshipProgram.__dataclass_fields__.keys())
        defaults = {k: v for k, v in defaults.items() if k in valid}
    return InternshipProgram(**defaults)


# --- Tests Décomposition du Score & KPI ---

def test_explain_score_eligible_perfect():
    prof = _make_sample_profile()
    prog = _make_sample_program()
    bd = explain_score(prof, prog)
    assert bd.eligible is True
    assert bd.base_points == 50
    assert bd.interest_points == 30
    assert bd.location_points == 10
    assert bd.paid_points == 10
    assert bd.total == 100
    assert "corporate_finance" in bd.shared_interests


def test_explain_score_ineligible_returns_zero_and_action():
    prof = _make_sample_profile(current_year=1, us_work_auth=False)
    prog = _make_sample_program(min_year=3, requires_us_auth=True)
    bd = explain_score(prof, prog)
    assert bd.eligible is False
    assert bd.total == 0
    assert bd.base_points == 0
    assert len(bd.reasons) >= 1
    assert bd.action_hint != ""


def test_build_action_hint_year_and_us_auth():
    prog = _make_sample_program(min_year=2, requires_us_auth=True)
    hint = build_action_hint(["Requiert 2e année minimum", "Autorisation US requise"], prog)
    assert "2e année" in hint
    assert "US" in hint


def test_compute_kpis_counts():
    prof = _make_sample_profile()
    p1 = _make_sample_program(id="p1", deadline=date(2026, 11, 18), locations=["Montréal"])
    p2 = _make_sample_program(id="p2", min_year=3, deadline=date(2026, 12, 25), locations=["Toronto"])
    kpis = compute_kpis(prof, [p1, p2], today=date(2026, 11, 10))
    assert kpis["total_count"] == 2
    assert kpis["eligible_count"] == 1
    assert kpis["montreal_count"] == 1
    assert kpis["deadlines_30d"] == 1
    assert kpis["next_deadline_days"] == 8


# --- Tests Onboarding Conversationnel ---

def test_parse_year_variants():
    assert parse_year("1") == 1
    assert parse_year("Je suis en 2e année") == 2
    assert parse_year("première année") == 1
    assert parse_year("texte sans chiffre") is None


def test_parse_graduation_formats():
    assert parse_graduation("2029-05") == "2029-05-15"
    assert parse_graduation("Mai 2029") == "2029-05-15"
    assert parse_graduation("05/2028") == "2028-05-15"
    assert parse_graduation("invalid") is None


def test_parse_interests_and_all():
    tags = parse_interests("quant, venture_capital et ia")
    assert "quant" in tags
    assert "venture_capital" in tags
    assert "ai" in tags
    all_tags = parse_interests("tous")
    assert len(all_tags) >= 9


def test_parse_us_auth():
    assert parse_us_auth("Oui") is True
    assert parse_us_auth("non pas encore") is False
    assert parse_us_auth("peut-être") is None


def test_full_onboarding_flow():
    ans = {}
    step, ans, _ = process_onboarding_step(0, "1re année", ans)
    assert step == 1 and ans["current_year"] == 1

    step, ans, _ = process_onboarding_step(1, "2029-05", ans)
    assert step == 2 and ans["graduation"] == "2029-05-15"

    step, ans, _ = process_onboarding_step(2, "quant, markets", ans)
    assert step == 3 and "quant" in ans["interests"]

    step, ans, _ = process_onboarding_step(3, "Montréal", ans)
    assert step == 4 and ans["home_base"] == "Montréal"

    step, ans, reply = process_onboarding_step(4, "non", ans)
    assert step == 5 and ans["us_work_auth"] is False
    assert "Voici ton profil" in reply

    built = build_profile_from_answers(ans)
    assert built.current_year == 1
    assert built.us_work_auth is False


# --- Tests Tracker SQLite & CSV ---

def test_sqlite_tracker_crud_and_csv(tmp_path: Path):
    db_file = tmp_path / "test_tracker.db"
    init_db(db_file)

    set_application_status("bnp-credit", "Postulé", "CV envoyé le 10 nov", db_path=db_file)
    entry = get_application("bnp-credit", db_path=db_file)
    assert entry["status"] == "Postulé"
    assert entry["notes"] == "CV envoyé le 10 nov"

    # Mise à jour
    set_application_status("bnp-credit", "Entretien", "1er tour RH", db_path=db_file)
    all_items = get_all_tracked(db_path=db_file)
    assert all_items["bnp-credit"]["status"] == "Entretien"

    # Export CSV
    prog = _make_sample_program(id="bnp-credit", firm="BNP Paribas", program="Credit Analyst")
    csv_text = export_tracked_to_csv([prog], db_path=db_file)
    assert "BNP Paribas" in csv_text
    assert "Entretien" in csv_text
    assert "1er tour RH" in csv_text

    # Remise à "Non suivi" sans note supprime l'entrée
    set_application_status("bnp-credit", "Non suivi", "", db_path=db_file)
    assert "bnp-credit" not in get_all_tracked(db_path=db_file)


def test_sqlite_tracker_rejects_invalid_status(tmp_path: Path):
    db_file = tmp_path / "test_invalid.db"
    with pytest.raises(ValueError):
        set_application_status("prog-1", "StatutInventé", db_path=db_file)