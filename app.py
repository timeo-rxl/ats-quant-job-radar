# app.py
"""ATS Quant Job Radar v2.1 — Application Streamlit bilingue (FR / EN)."""

from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Any, List
import html

import streamlit as st

import radar.data as radar_data
from radar.i18n import (
    t,
    format_year_label,
    status_to_display,
)
from radar.onboarding import (
    AVAILABLE_INTERESTS,
    get_questions,
    process_onboarding_step,
    build_profile_from_answers,
)
from radar.scoring import (
    explain_score,
    compute_kpis,
    _safe_deadline_status,
    _safe_days_until,
)
from radar.tracker import (
    VALID_STATUSES,
    get_all_tracked,
    set_application_status,
    export_tracked_to_csv,
)


def _load_dataset() -> tuple[Any, List[Any]]:
    base = Path(__file__).resolve().parent
    profile_path = base / "my_profile.yaml"
    programs_path = base / "data/programs.yaml"

    if hasattr(radar_data, "load_profile"):
        default_profile = radar_data.load_profile(profile_path)
    elif hasattr(radar_data, "load_user_profile"):
        default_profile = radar_data.load_user_profile(profile_path)
    else:
        raise RuntimeError("Fonction de chargement de profil introuvable dans radar.data")

    if hasattr(radar_data, "load_programs"):
        programs = radar_data.load_programs(programs_path)
    elif hasattr(radar_data, "load_all_programs"):
        programs = radar_data.load_all_programs(programs_path)
    else:
        raise RuntimeError("Fonction de chargement des programmes introuvable dans radar.data")

    return default_profile, list(programs)


RALLYO_CSS = """
<style>
    :root {
        --navy: #0B1B33;
        --navy-light: #162B4D;
        --orange: #FF5A1F;
        --orange-soft: #FFF0EB;
        --bg-light: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-main: #0F172A;
        --text-muted: #475569;
        --border-color: #E2E8F0;
    }

    .stApp {
        background-color: var(--bg-light);
    }

    /* Hero Banner */
    .radar-hero {
        background: linear-gradient(135deg, #0B1B33 0%, #162B4D 100%);
        color: #FFFFFF;
        padding: 2rem 2.2rem;
        border-radius: 16px;
        border-bottom: 4px solid #FF5A1F;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(11, 27, 51, 0.12);
    }
    .radar-hero h1 {
        color: #FFFFFF !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    .radar-hero p {
        color: #CBD5E1;
        font-size: 1.05rem;
        margin: 0;
        max-width: 780px;
    }
    .hero-tag {
        display: inline-block;
        background-color: #FF5A1F;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.75rem;
        letter-spacing: 0.05em;
    }

    /* KPI Cards */
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-top: 4px solid var(--navy);
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        height: 100%;
    }
    .kpi-card.accent {
        border-top-color: var(--orange);
    }
    .kpi-label {
        color: var(--text-muted);
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        color: var(--navy);
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0.2rem 0;
    }
    .kpi-sub {
        color: var(--text-muted);
        font-size: 0.8rem;
    }

    /* Urgent Spotlight */
    .urgent-banner {
        background: #FFF7ED;
        border-left: 5px solid #FF5A1F;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 1rem 0 1.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.75rem;
    }

    /* Program Cards */
    .prog-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 6px rgba(11, 27, 51, 0.04);
    }
    .prog-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .prog-firm {
        color: #FF5A1F;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .prog-title {
        color: #0B1B33;
        font-weight: 800;
        font-size: 1.2rem;
        margin: 0.1rem 0 0.4rem 0;
    }
    .score-pill {
        background: #0B1B33;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.1rem;
        padding: 0.4rem 0.9rem;
        border-radius: 10px;
        border: 2px solid #FF5A1F;
        white-space: nowrap;
    }
    .score-pill.zero {
        background: #F1F5F9;
        color: #64748B;
        border-color: #CBD5E1;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .badge-open { background: #DCFCE7; color: #166534; }
    .badge-urgent { background: #FFEDD5; color: #C2410C; border: 1px solid #FF5A1F; }
    .badge-closed { background: #F1F5F9; color: #475569; }
    .badge-watch { background: #E0F2FE; color: #075985; }
    .badge-unverified { background: #FEF3C7; color: #92400E; }
    .badge-verified { background: #E0E7FF; color: #1E40AF; }

    /* Honesty Notice */
    .honesty-box {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 4px solid #0B1B33;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.88rem;
        color: #334155;
        margin-bottom: 1.25rem;
    }
</style>
"""


def _status_badge_html(status: str, days_left: int | None, lang: str) -> str:
    st_low = status.lower()
    if st_low == "urgent":
        lbl = (
            t("badge_urgent_days", lang, days=days_left)
            if days_left is not None
            else t("badge_urgent", lang)
        )
        return f'<span class="badge badge-urgent">{html.escape(lbl)}</span>'
    if st_low == "open":
        lbl = (
            t("badge_open_days", lang, days=days_left)
            if days_left is not None
            else t("badge_open", lang)
        )
        return f'<span class="badge badge-open">{html.escape(lbl)}</span>'
    if st_low == "closed":
        return f'<span class="badge badge-closed">{html.escape(t("badge_closed", lang))}</span>'
    return f'<span class="badge badge-watch">{html.escape(t("badge_watch", lang))}</span>'


def _init_session_state(default_profile: Any) -> None:
    if "lang" not in st.session_state:
        st.session_state.lang = "fr"
    if "active_profile" not in st.session_state:
        st.session_state.active_profile = default_profile
    if "using_custom_profile" not in st.session_state:
        st.session_state.using_custom_profile = False
    if "show_onboarding" not in st.session_state:
        st.session_state.show_onboarding = False
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 0
    if "onboarding_answers" not in st.session_state:
        st.session_state.onboarding_answers = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": get_questions(st.session_state.lang)[0]}
        ]


def _reset_onboarding(lang: str) -> None:
    st.session_state.show_onboarding = True
    st.session_state.onboarding_step = 0
    st.session_state.onboarding_answers = {}
    st.session_state.chat_history = [
        {"role": "assistant", "content": get_questions(lang)[0]}
    ]


def main() -> None:
    st.set_page_config(
        page_title="ATS Quant Job Radar v2.1",
        page_icon="🎯",
        layout="wide",
    )
    st.markdown(RALLYO_CSS, unsafe_allow_html=True)

    default_profile, programs = _load_dataset()
    _init_session_state(default_profile)

    # -----------------------------------------------------------------------
    # SÉLECTEUR DE LANGUE (Tout en haut de la sidebar — persistant sans reset du profil)
    # -----------------------------------------------------------------------
    lang_options = {"fr": "🇫🇷 Français", "en": "🇬🇧 English"}
    current_lang = st.session_state.lang
    selected_lang = st.sidebar.radio(
        t("lang_selector_label", current_lang),
        options=["fr", "en"],
        format_func=lambda code: lang_options[code],
        index=0 if current_lang == "fr" else 1,
        horizontal=True,
    )
    if selected_lang != current_lang:
        st.session_state.lang = selected_lang
        # Si l'utilisateur n'a pas encore commencé à répondre dans le chat (étape 0, 1 seul message),
        # on met à jour la première question d'accueil dans la nouvelle langue choisie.
        if (
            st.session_state.onboarding_step == 0
            and len(st.session_state.chat_history) == 1
        ):
            st.session_state.chat_history = [
                {"role": "assistant", "content": get_questions(selected_lang)[0]}
            ]
        st.rerun()

    lang = st.session_state.lang
    profile = st.session_state.active_profile
    today = date.today()

    # -----------------------------------------------------------------------
    # HERO BANNER
    # -----------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="radar-hero">
            <span class="hero-tag">{html.escape(t("hero_tag", lang))}</span>
            <h1>{html.escape(t("hero_title", lang))}</h1>
            <p>{html.escape(t("hero_subtitle", lang))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_col1, hero_col2, hero_col3 = st.columns([2, 2, 4])
    with hero_col1:
        if st.button(t("btn_find_internships", lang), type="primary", use_container_width=True):
            _reset_onboarding(lang)
            st.rerun()
    with hero_col2:
        if st.session_state.using_custom_profile:
            if st.button(t("btn_reset_profile", lang), use_container_width=True):
                st.session_state.active_profile = default_profile
                st.session_state.using_custom_profile = False
                st.session_state.show_onboarding = False
                st.rerun()
        else:
            if st.button(t("btn_edit_profile", lang), use_container_width=True):
                _reset_onboarding(lang)
                st.rerun()
    with hero_col3:
        prof_name = getattr(profile, "name", "Profil")
        prof_yr = int(getattr(profile, "current_year", 1))
        prof_grad = str(getattr(profile, "graduation", ""))[:7]
        prof_city = getattr(profile, "home_base", "Montréal")
        prof_us = t("yes", lang) if getattr(profile, "us_work_auth", False) else t("no", lang)
        st.info(
            t(
                "active_profile_banner",
                lang,
                name=prof_name,
                year_label=format_year_label(prof_yr, lang),
                grad=prof_grad,
                city=prof_city,
                us=prof_us,
            )
        )

    # -----------------------------------------------------------------------
    # A. ONBOARDING CONVERSATIONNEL BILINGUE AVEC AVATAR « RADAR »
    # -----------------------------------------------------------------------
    if st.session_state.show_onboarding:
        with st.container(border=True):
            st.subheader(t("onboarding_title", lang))
            st.caption(t("onboarding_caption", lang))

            for msg in st.session_state.chat_history:
                avatar = "🎯" if msg["role"] == "assistant" else "🧑‍🎓"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

            step = st.session_state.onboarding_step

            if step == 2:
                st.caption(
                    t("onboarding_tags_hint", lang)
                    + ", ".join(f"`{tag}`" for tag in AVAILABLE_INTERESTS)
                )

            if step < 5:
                user_msg = st.chat_input(t("chat_input_placeholder", lang))
                if user_msg:
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    next_step, updated_ans, reply = process_onboarding_step(
                        step,
                        user_msg,
                        st.session_state.onboarding_answers,
                        lang=lang,
                    )
                    st.session_state.onboarding_step = next_step
                    st.session_state.onboarding_answers = updated_ans
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

                    if next_step == 5:
                        new_prof = build_profile_from_answers(updated_ans, default_profile, lang=lang)
                        st.session_state.active_profile = new_prof
                        st.session_state.using_custom_profile = True
                    st.rerun()
            else:
                col_done1, col_done2 = st.columns([1, 1])
                with col_done1:
                    if st.button(t("btn_see_results", lang), type="primary", use_container_width=True):
                        st.session_state.show_onboarding = False
                        st.rerun()
                with col_done2:
                    if st.button(t("btn_restart_onboarding", lang), use_container_width=True):
                        _reset_onboarding(lang)
                        st.rerun()

    # -----------------------------------------------------------------------
    # B. TABLEAU DE BORD KPI
    # -----------------------------------------------------------------------
    kpis = compute_kpis(profile, programs, today)

    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.markdown(
            f"""
            <div class="kpi-card accent">
                <div class="kpi-label">{html.escape(t("kpi_eligible_label", lang))}</div>
                <div class="kpi-value">{kpis['eligible_count']} / {kpis['total_count']}</div>
                <div class="kpi-sub">{html.escape(t("kpi_eligible_sub", lang))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{html.escape(t("kpi_deadlines_label", lang))}</div>
                <div class="kpi-value">{kpis['deadlines_30d']}</div>
                <div class="kpi-sub">{html.escape(t("kpi_deadlines_sub", lang))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col3:
        nxt_days = kpis["next_deadline_days"]
        nxt_str = (
            t("kpi_next_days", lang, days=nxt_days)
            if nxt_days is not None
            else t("kpi_next_none", lang)
        )
        st.markdown(
            f"""
            <div class="kpi-card accent">
                <div class="kpi-label">{html.escape(t("kpi_next_label", lang))}</div>
                <div class="kpi-value">{html.escape(nxt_str)}</div>
                <div class="kpi-sub">{html.escape(t("kpi_next_sub", lang))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{html.escape(t("kpi_montreal_label", lang))}</div>
                <div class="kpi-value">{kpis['montreal_count']}</div>
                <div class="kpi-sub">{html.escape(t("kpi_montreal_sub", lang))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Mise en avant « Prochaine échéance »
    urgent_prog = kpis["most_urgent_program"]
    if urgent_prog is not None:
        u_firm = html.escape(str(getattr(urgent_prog, "firm", "")))
        u_title = html.escape(str(getattr(urgent_prog, "program", "")))
        u_dl = html.escape(str(getattr(urgent_prog, "deadline", "")))
        u_days = kpis["next_deadline_days"]
        u_url = html.escape(str(getattr(urgent_prog, "apply_url", "#")))
        u_info_html = t("urgent_deadline_info", lang, deadline=u_dl, days=u_days)
        st.markdown(
            f"""
            <div class="urgent-banner">
                <div>
                    <strong>{html.escape(t("urgent_prefix", lang))}</strong> {u_firm} — <strong>{u_title}</strong>
                    {u_info_html}
                </div>
                <div>
                    <a href="{u_url}" target="_blank" style="background:#FF5A1F;color:#FFF;padding:0.45rem 0.95rem;border-radius:8px;text-decoration:none;font-weight:700;">
                        {html.escape(t("urgent_cta", lang))}
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Graphiques natifs : répartition par catégorie et par statut de deadline
    with st.expander(t("charts_expander", lang), expanded=False):
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.markdown(t("chart_by_category", lang))
            st.bar_chart(kpis["by_category"], color="#0B1B33")
        with g_col2:
            st.markdown(t("chart_by_status", lang))
            status_localized = {
                t("status_open_chart", lang): kpis["by_status"].get("open", 0),
                t("status_urgent_chart", lang): kpis["by_status"].get("urgent", 0),
                t("status_watch_chart", lang): kpis["by_status"].get("watch", 0),
                t("status_closed_chart", lang): kpis["by_status"].get("closed", 0),
            }
            st.bar_chart(status_localized, color="#FF5A1F")

    # Bandeau d'honnêteté sur les données
    verified_total = sum(1 for p in programs if getattr(p, "verified", False))
    unverified_total = len(programs) - verified_total
    st.markdown(
        f'<div class="honesty-box">{t("honesty_box_html", lang, total=len(programs), verified=verified_total, unverified=unverified_total)}</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # FILTRES EN SIDEBAR
    # -----------------------------------------------------------------------
    st.sidebar.divider()
    st.sidebar.header(t("sidebar_header", lang))

    all_sessions = sorted({s for p in programs for s in (getattr(p, "sessions", []) or [])})
    all_categories = sorted({str(getattr(p, "category", "")) for p in programs if getattr(p, "category", "")})
    all_locations = sorted({loc for p in programs for loc in (getattr(p, "locations", []) or [])})

    all_f_label = t("filter_all_f", lang)
    all_m_label = t("filter_all_m", lang)

    search_query = st.sidebar.text_input(t("filter_search", lang), value="")
    selected_session = st.sidebar.selectbox(t("filter_session", lang), [all_f_label] + all_sessions)
    selected_category = st.sidebar.selectbox(t("filter_category", lang), [all_f_label] + all_categories)
    selected_location = st.sidebar.selectbox(t("filter_location", lang), [all_m_label] + all_locations)

    only_paid = st.sidebar.checkbox(t("filter_only_paid", lang), value=False)
    only_eligible = st.sidebar.checkbox(t("filter_only_eligible", lang), value=False)
    only_first_year = st.sidebar.checkbox(t("filter_only_first_year", lang), value=False)

    # Filtrage des programmes
    filtered_programs: List[tuple[Any, Any]] = []
    for prog in programs:
        bd = explain_score(profile, prog, lang=lang)

        if selected_session != all_f_label and selected_session not in (getattr(prog, "sessions", []) or []):
            continue
        if selected_category != all_f_label and str(getattr(prog, "category", "")) != selected_category:
            continue
        if selected_location != all_m_label and selected_location not in (getattr(prog, "locations", []) or []):
            continue
        if only_paid and not getattr(prog, "paid", False):
            continue
        if only_eligible and not bd.eligible:
            continue
        if only_first_year and getattr(prog, "min_year", 1) > 1:
            continue
        if search_query.strip():
            q = search_query.strip().lower()
            haystack = f"{getattr(prog, 'firm', '')} {getattr(prog, 'program', '')} {getattr(prog, 'category', '')} {getattr(prog, 'notes', '')}".lower()
            if q not in haystack:
                continue

        filtered_programs.append((prog, bd))

    filtered_programs.sort(key=lambda item: (-item[1].total, str(getattr(item[0], "firm", ""))))

    # -----------------------------------------------------------------------
    # NAVIGATION PAR ONGLETS : PROGRAMMES / CE QUI TE BLOQUE / SUIVI SQLITE
    # -----------------------------------------------------------------------
    tracked_map = get_all_tracked()

    tab_all, tab_blockers, tab_tracker = st.tabs([
        t("tab_programs", lang, count=len(filtered_programs)),
        t("tab_blockers", lang),
        t("tab_tracker", lang, count=len(tracked_map)),
    ])

    # --- ONGLET 1 : PROGRAMMES & SCORE EXPLIQUÉ ---
    with tab_all:
        if not filtered_programs:
            st.warning(t("no_programs_match", lang))
        for prog, bd in filtered_programs:
            pid = str(getattr(prog, "id", f"{getattr(prog, 'firm', '')}-{getattr(prog, 'program', '')}"))
            firm = str(getattr(prog, "firm", ""))
            title = str(getattr(prog, "program", ""))
            category = str(getattr(prog, "category", ""))
            locs = ", ".join(getattr(prog, "locations", []) or [])
            is_verified = bool(getattr(prog, "verified", False))

            st_code = _safe_deadline_status(prog, today)
            d_left = _safe_days_until(prog, today)

            badge_html = _status_badge_html(st_code, d_left, lang)
            verif_html = (
                f'<span class="badge badge-verified">{html.escape(t("badge_verified", lang))}</span>'
                if is_verified
                else f'<span class="badge badge-unverified">{html.escape(t("badge_unverified", lang))}</span>'
            )
            score_cls = "score-pill" if bd.eligible else "score-pill zero"

            st.markdown(
                f"""
                <div class="prog-card">
                    <div class="prog-header">
                        <div>
                            <div class="prog-firm">{html.escape(firm)} • {html.escape(category)}</div>
                            <div class="prog-title">{html.escape(title)}</div>
                            <div>
                                {badge_html}
                                {verif_html}
                                <span class="badge badge-closed">📍 {html.escape(locs)}</span>
                            </div>
                        </div>
                        <div class="{score_cls}">
                            {bd.total} / 100
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(t("expander_program_details", lang, firm=firm, title=title)):
                c_left, c_right = st.columns([3, 2])
                with c_left:
                    if bd.eligible:
                        st.markdown(t("eligible_header", lang))
                        st.progress(bd.total / 100.0)
                        tags_str = (
                            "(" + ", ".join(bd.shared_interests) + ")"
                            if bd.shared_interests
                            else t("no_shared_tags", lang)
                        )
                        st.markdown(
                            "\n".join([
                                t("score_base_line", lang, pts=bd.base_points),
                                t("score_interests_line", lang, count=len(bd.shared_interests), pts=bd.interest_points, tags=tags_str),
                                t("score_location_line", lang, city=getattr(profile, "home_base", ""), pts=bd.location_points),
                                t("score_paid_line", lang, pts=bd.paid_points),
                                t("score_total_line", lang, total=bd.total),
                            ])
                        )
                    else:
                        st.markdown(t("ineligible_header", lang))
                        for r in bd.reasons:
                            st.error(f"• {r}")
                        st.info(t("recommended_action_label", lang, hint=bd.action_hint))

                    dl_val = getattr(prog, "deadline", None) or t("deadline_unspecified", lang)
                    dl_note = getattr(prog, "deadline_note", None) or ""
                    notes_txt = getattr(prog, "notes", None) or ""
                    st.markdown(
                        t(
                            "deadline_label",
                            lang,
                            dl=dl_val,
                            note=f"— *{dl_note}*" if dl_note else "",
                        )
                    )
                    if notes_txt:
                        st.caption(t("note_prefix", lang, notes=notes_txt))

                    apply_url = getattr(prog, "apply_url", None)
                    if apply_url:
                        st.link_button(t("btn_official_apply", lang), str(apply_url))

                with c_right:
                    st.markdown(t("track_section_header", lang))
                    current_track = tracked_map.get(pid, {"status": "Non suivi", "notes": ""})
                    cur_status_fr = (
                        current_track["status"]
                        if current_track["status"] in VALID_STATUSES
                        else "Non suivi"
                    )

                    new_status_fr = st.selectbox(
                        t("track_status_label", lang),
                        options=VALID_STATUSES,
                        format_func=lambda s: status_to_display(s, lang=lang),
                        index=VALID_STATUSES.index(cur_status_fr),
                        key=f"status_{pid}",
                    )
                    new_note = st.text_input(
                        t("track_note_label", lang),
                        value=current_track.get("notes", ""),
                        placeholder=t("track_note_placeholder", lang),
                        key=f"note_{pid}",
                    )
                    if st.button(t("btn_save_tracking", lang), key=f"save_{pid}", use_container_width=True):
                        set_application_status(pid, new_status_fr, new_note)
                        st.success(t("msg_tracking_saved", lang))
                        st.rerun()

    # --- ONGLET 2 : VUE « CE QUI TE BLOQUE » ---
    with tab_blockers:
        st.subheader(t("blockers_header", lang))
        st.caption(t("blockers_caption", lang))

        ineligible_list = [(p, explain_score(profile, p, lang=lang)) for p in programs]
        ineligible_list = [(p, b) for p, b in ineligible_list if not b.eligible]

        if not ineligible_list:
            st.success(t("blockers_none", lang))
        else:
            for prog, bd in ineligible_list:
                firm = str(getattr(prog, "firm", ""))
                title = str(getattr(prog, "program", ""))
                reasons_str = " ; ".join(bd.reasons)
                with st.container(border=True):
                    b_col1, b_col2 = st.columns([3, 2])
                    with b_col1:
                        st.markdown(f"**{firm} — {title}**")
                        st.markdown(t("blocker_reason_prefix", lang, reasons=reasons_str))
                    with b_col2:
                        st.markdown(t("blocker_action_prefix", lang, hint=bd.action_hint))

    # --- ONGLET 3 : SUIVI DE CANDIDATURES (SQLITE + EXPORT CSV BILINGUE) ---
    with tab_tracker:
        st.subheader(t("tracker_tab_header", lang))
        csv_data = export_tracked_to_csv(programs, lang=lang)

        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.caption(t("tracker_tab_caption", lang))
        with t_col2:
            csv_filename = (
                f"radar_applications_{today.isoformat()}.csv"
                if lang == "en"
                else f"radar_candidatures_{today.isoformat()}.csv"
            )
            st.download_button(
                label=t("btn_export_csv", lang),
                data=csv_data.encode("utf-8"),
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True,
            )

        active_tracked = {
            k: v for k, v in tracked_map.items() if v["status"] != "Non suivi" or v["notes"].strip()
        }

        if not active_tracked:
            st.info(t("tracker_empty_msg", lang))
        else:
            prog_by_id = {str(getattr(p, "id", "")): p for p in programs}
            rows_display = []
            for pid, info in active_tracked.items():
                p_obj = prog_by_id.get(pid)
                rows_display.append({
                    t("col_firm", lang): getattr(p_obj, "firm", pid) if p_obj else pid,
                    t("col_program", lang): getattr(p_obj, "program", "") if p_obj else "",
                    t("col_status", lang): status_to_display(info["status"], lang=lang),
                    t("col_notes", lang): info["notes"],
                    t("col_updated", lang): info["updated_at"],
                })
            st.dataframe(rows_display, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()