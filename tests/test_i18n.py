# tests/test_i18n.py
"""Tests unitaires pour l'internationalisation (FR/EN), l'onboarding en anglais et le CSV bilingue."""

from datetime import date
from pathlib import Path

from radar.models import Profile, InternshipProgram
from radar.i18n import (
    STRINGS,
    t,
    format_year_label,
    status_to_display,
    status_from_input,
    translate_reason,
)
from radar.onboarding import (
    get_questions,
    parse_year,
    parse_graduation,
    parse_interests,
    parse_us_auth,
    process_onboarding_step,
    build_profile_from_answers,
)
from radar.scoring import explain_score
from radar.tracker import (
    init_db,
    set_application_status,
    get_application,
    export_tracked_to_csv,
)


def _sample_profile(**overrides) -> Profile:
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
        interests=["quant", "markets"],
    )
    defaults.update(overrides)
    return Profile(**defaults)


def _sample_program(**overrides) -> InternshipProgram:
    defaults = dict(
        id="prog-en-1",
        firm="Test Capital",
        program="Quant Intern",
        type="summer_internship",
        category="quant",
        locations=["Montréal", "New York"],
        remote=False,
        sessions=["Summer 2027"],
        paid=True,
        min_year=2,
        max_year=3,
        grad_not_before="2028-01",
        grad_window=None,
        requires_us_auth=True,
        interests=["quant", "markets"],
        deadline=date(2026, 11, 25),
        deadline_note="Rolling",
        apply_url="https://example.com",
        source="https://example.com",
        verified=True,
        verified_date="2026-10-01",
        search_hint="Test Capital quant",
        notes="",
    )
    defaults.update(overrides)
    return InternshipProgram(**defaults)


def test_all_i18n_keys_have_fr_and_en():
    for key, translations in STRINGS.items():
        assert "fr" in translations and translations["fr"], f"Missing FR for {key}"
        assert "en" in translations and translations["en"], f"Missing EN for {key}"


def test_t_fallback_and_formatting():
    assert t("btn_find_internships", "en") == "🎯 Find my internships (Radar Assistant)"
    assert t("btn_find_internships", "fr") == "🎯 Trouver mes stages (Assistant Radar)"
    # Fallback sur le français si langue inconnue
    assert t("btn_find_internships", "es") == "🎯 Trouver mes stages (Assistant Radar)"
    # Clé inconnue retourne la clé
    assert t("unknown_key_xyz", "en") == "unknown_key_xyz"
    # Formatage dynamique
    assert "30" in t("kpi_next_days", "en", days=30)


def test_format_year_label_bilingual():
    assert format_year_label(1, "fr") == "1re année"
    assert format_year_label(2, "fr") == "2e année"
    assert format_year_label(1, "en") == "1st year"
    assert format_year_label(2, "en") == "2nd year"
    assert format_year_label(3, "en") == "3rd year"


def test_translate_reason_fr_to_en():
    # Chaînes RÉELLES de radar/matching.py (pas de formulations inventées).
    r_us = translate_reason("exige une autorisation de travail aux États-Unis", lang="en")
    assert "US work authorization" in r_us

    r_yr = translate_reason("demande la 2e année minimum (profil : 1re année)", lang="en")
    assert "Year 2" in r_yr

    r_grad = translate_reason(
        "demande une diplomation à partir de 2028-01 (diplomation du profil : 2029-05)",
        lang="en",
    )
    assert "2028-01" in r_grad
    assert "Graduation" in r_grad

    r_win = translate_reason(
        "demande une diplomation entre 2027-12 et 2028-12 (diplomation du profil : 2029-05)",
        lang="en",
    )
    assert "2027-12" in r_win and "2028-12" in r_win
    assert "Graduation window" in r_win

    # En français, la chaîne reste intacte
    orig = "exige une autorisation de travail aux États-Unis"
    assert translate_reason(orig, lang="fr") == orig


def test_english_year_parsing():
    assert parse_year("1st year") == 1
    assert parse_year("I am a freshman") == 1
    assert parse_year("sophomore") == 2
    assert parse_year("2nd year") == 2
    assert parse_year("junior") == 3
    assert parse_year("3rd year") == 3
    assert parse_year("senior") == 4
    assert parse_year("4th year") == 4


def test_english_graduation_months():
    assert parse_graduation("May 2029") == "2029-05-15"
    assert parse_graduation("June 2028") == "2028-06-15"
    assert parse_graduation("December 2027") == "2027-12-15"
    assert parse_graduation("Aug 2029") == "2029-08-15"


def test_english_interests_and_us_auth():
    tags = parse_interests("banking, trading, vc, software")
    assert "investment_banking" in tags
    assert "markets" in tags
    assert "venture_capital" in tags
    assert "tech" in tags

    assert len(parse_interests("all")) == 10
    assert parse_us_auth("yes") is True
    assert parse_us_auth("no") is False


def test_full_onboarding_flow_in_english():
    q_en = get_questions("en")
    assert "Question 1/5" in q_en[0]

    ans = {}
    step, ans, reply = process_onboarding_step(0, "freshman", ans, lang="en")
    assert step == 1 and ans["current_year"] == 1
    assert "Question 2/5" in reply

    step, ans, reply = process_onboarding_step(1, "May 2029", ans, lang="en")
    assert step == 2 and ans["graduation"] == "2029-05-15"

    step, ans, reply = process_onboarding_step(2, "quant, banking, ai", ans, lang="en")
    assert step == 3 and "investment_banking" in ans["interests"]

    step, ans, reply = process_onboarding_step(3, "Montréal, New York", ans, lang="en")
    assert step == 4 and ans["home_base"] == "Montréal"

    step, ans, summary = process_onboarding_step(4, "no", ans, lang="en")
    assert step == 5 and ans["us_work_auth"] is False
    assert "Here is your profile:" in summary
    assert "1st year" in summary

    prof = build_profile_from_answers(ans, lang="en")
    assert prof.current_year == 1
    assert isinstance(prof.graduation, date)
    assert prof.graduation == date(2029, 5, 15)


def test_explain_score_english_reasons_and_hints():
    prof = _sample_profile(current_year=1, us_work_auth=False)
    prog = _sample_program(min_year=2, requires_us_auth=True)
    bd_en = explain_score(prof, prog, lang="en")
    assert bd_en.eligible is False
    assert bd_en.total == 0
    assert any("Year 2" in r or "US work authorization" in r for r in bd_en.reasons)
    assert "Year 2" in bd_en.action_hint or "US work authorization" in bd_en.action_hint


def test_tracker_bilingual_status_and_csv_headers(tmp_path: Path):
    db_file = tmp_path / "test_bilingual.db"
    init_db(db_file)

    # On peut sauvegarder en passant le statut anglais : il est stocké en français canonique en base
    set_application_status("prog-en-1", "Applied", "Submitted via portal", db_path=db_file)
    saved = get_application("prog-en-1", db_path=db_file)
    assert saved["status"] == "Postulé"
    assert status_to_display(saved["status"], lang="en") == "Applied"
    assert status_from_input("Interview") == "Entretien"

    prog = _sample_program(id="prog-en-1", firm="Test Capital", program="Quant Intern")

    # Export CSV en français
    csv_fr = export_tracked_to_csv([prog], db_path=db_file, lang="fr")
    assert "ID Programme,Entreprise,Programme" in csv_fr
    assert "Postulé" in csv_fr

    # Export CSV en anglais
    csv_en = export_tracked_to_csv([prog], db_path=db_file, lang="en")
    assert "Program ID,Firm,Program,Category,Locations,Status" in csv_en
    assert "Applied" in csv_en