# app.py
"""ATS Quant Job Radar v2.0 — Application Streamlit principale."""

from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Any, List
import html

import streamlit as st

import radar.data as radar_data
from radar.onboarding import (
    QUESTIONS,
    AVAILABLE_INTERESTS,
    INTEREST_LABELS_FR,
    process_onboarding_step,
    build_profile_from_answers,
    format_profile_summary,
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


# ---------------------------------------------------------------------------
# Chargement résilient des données (compatible avec toutes les variantes de radar/data.py)
# ---------------------------------------------------------------------------
def _load_dataset() -> tuple[Any, List[Any]]:
    base = Path(__file__).resolve().parent
    profile_path = base / "my_profile.yaml"
    programs_path = base / "data" / "programs.yaml"

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


# ---------------------------------------------------------------------------
# Style CSS (Palette Rallyo : Bleu nuit #0B1B33 + Orange vif #FF5A1F)
# ---------------------------------------------------------------------------
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


def _status_badge_html(status: str, days_left: int | None) -> str:
    st_low = status.lower()
    if st_low == "urgent":
        lbl = f"🔥 Ferme bientôt ({days_left} j)" if days_left is not None else "🔥 Ferme bientôt"
        return f'<span class="badge badge-urgent">{html.escape(lbl)}</span>'
    if st_low == "open":
        lbl = f"✅ Ouvert ({days_left} j)" if days_left is not None else "✅ Ouvert"
        return f'<span class="badge badge-open">{html.escape(lbl)}</span>'
    if st_low == "closed":
        return '<span class="badge badge-closed">🔒 Fermé</span>'
    return '<span class="badge badge-watch">👀 À surveiller</span>'


def _init_session_state(default_profile: Any) -> None:
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
            {"role": "assistant", "content": QUESTIONS[0]}
        ]


def _reset_onboarding() -> None:
    st.session_state.show_onboarding = True
    st.session_state.onboarding_step = 0
    st.session_state.onboarding_answers = {}
    st.session_state.chat_history = [
        {"role": "assistant", "content": QUESTIONS[0]}
    ]


def main() -> None:
    st.set_page_config(
        page_title="ATS Quant Job Radar v2.0",
        page_icon="🎯",
        layout="wide",
    )
    st.markdown(RALLYO_CSS, unsafe_allow_html=True)

    default_profile, programs = _load_dataset()
    _init_session_state(default_profile)
    profile = st.session_state.active_profile
    today = date.today()

    # -----------------------------------------------------------------------
    # HERO BANNER
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div class="radar-hero">
            <span class="hero-tag">Radar v2.0 • Finance, Quant & Tech</span>
            <h1>🎯 ATS Quant Job Radar</h1>
            <p>Identifie instantanément les programmes de stages auxquels tu es réellement admissible selon ton année d'études, ta date de diplomation et ton statut de visa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_col1, hero_col2, hero_col3 = st.columns([2, 2, 4])
    with hero_col1:
        if st.button("🎯 Trouver mes stages (Assistant Radar)", type="primary", use_container_width=True):
            _reset_onboarding()
            st.rerun()
    with hero_col2:
        if st.session_state.using_custom_profile:
            if st.button("🔄 Revenir au profil d'exemple", use_container_width=True):
                st.session_state.active_profile = default_profile
                st.session_state.using_custom_profile = False
                st.session_state.show_onboarding = False
                st.rerun()
        else:
            if st.button("✏️ Modifier mon profil", use_container_width=True):
                _reset_onboarding()
                st.rerun()
    with hero_col3:
        prof_name = getattr(profile, "name", "Profil")
        prof_yr = getattr(profile, "current_year", 1)
        yr_str = "1re année" if prof_yr == 1 else f"{prof_yr}e année"
        prof_grad = str(getattr(profile, "graduation", ""))[:7]
        prof_city = getattr(profile, "home_base", "Montréal")
        prof_us = "Oui" if getattr(profile, "us_work_auth", False) else "Non"
        st.info(
            f"**Profil actif :** {prof_name} • {yr_str} • Diplomation `{prof_grad}` • Base : **{prof_city}** • Autorisation US : **{prof_us}**"
        )

    # -----------------------------------------------------------------------
    # A. ONBOARDING CONVERSATIONNEL AVEC AVATAR « RADAR »
    # -----------------------------------------------------------------------
    if st.session_state.show_onboarding:
        with st.container(border=True):
            st.subheader("🎯 Onboarding interactif avec Radar")
            st.caption("Réponds aux 5 questions une par une dans le chat ci-dessous (100 % local, sans clé API).")

            for msg in st.session_state.chat_history:
                avatar = "🎯" if msg["role"] == "assistant" else "🧑‍🎓"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

            step = st.session_state.onboarding_step

            # Raccourcis visuels optionnels pour faciliter la saisie sur mobile
            if step == 2:
                st.caption("💡 Tags disponibles : " + ", ".join(f"`{t}`" for t in AVAILABLE_INTERESTS))

            if step < 5:
                user_msg = st.chat_input("Écris ta réponse ici...")
                if user_msg:
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    next_step, updated_ans, reply = process_onboarding_step(
                        step,
                        user_msg,
                        st.session_state.onboarding_answers,
                    )
                    st.session_state.onboarding_step = next_step
                    st.session_state.onboarding_answers = updated_ans
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})

                    if next_step == 5:
                        new_prof = build_profile_from_answers(updated_ans, default_profile)
                        st.session_state.active_profile = new_prof
                        st.session_state.using_custom_profile = True
                    st.rerun()
            else:
                col_done1, col_done2 = st.columns([1, 1])
                with col_done1:
                    if st.button("✅ Voir mes résultats personnalisés", type="primary", use_container_width=True):
                        st.session_state.show_onboarding = False
                        st.rerun()
                with col_done2:
                    if st.button("🔁 Recommencer les 5 questions", use_container_width=True):
                        _reset_onboarding()
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
                <div class="kpi-label">Programmes admissibles</div>
                <div class="kpi-value">{kpis['eligible_count']} / {kpis['total_count']}</div>
                <div class="kpi-sub">Selon ton année, diplomation & visa</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Deadlines ≤ 30 jours</div>
                <div class="kpi-value">{kpis['deadlines_30d']}</div>
                <div class="kpi-sub">Programmes ouverts à candidater</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col3:
        nxt_days = kpis["next_deadline_days"]
        nxt_str = f"J-{nxt_days}" if nxt_days is not None else "Aucune fixe"
        st.markdown(
            f"""
            <div class="kpi-card accent">
                <div class="kpi-label">Prochaine deadline</div>
                <div class="kpi-value">{nxt_str}</div>
                <div class="kpi-sub">Compte à rebours prioritaire</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k_col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Bureaux à Montréal</div>
                <div class="kpi-value">{kpis['montreal_count']}</div>
                <div class="kpi-sub">Opportunités locales recensées</div>
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
        st.markdown(
            f"""
            <div class="urgent-banner">
                <div>
                    <strong>⚡ Prochaine échéance :</strong> {u_firm} — <strong>{u_title}</strong>
                    (Date limite : <code>{u_dl}</code>, dans <strong>{u_days} jour(s)</strong>)
                </div>
                <div>
                    <a href="{u_url}" target="_blank" style="background:#FF5A1F;color:#FFF;padding:0.45rem 0.95rem;border-radius:8px;text-decoration:none;font-weight:700;">
                        Postuler sur le site officiel ↗
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Graphiques natifs : répartition par catégorie et par statut de deadline
    with st.expander("📊 Voir la répartition du marché (Catégories & Statuts des deadlines)", expanded=False):
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.markdown("**Programmes par catégorie**")
            st.bar_chart(kpis["by_category"], color="#0B1B33")
        with g_col2:
            st.markdown("**Programmes par statut de deadline**")
            status_fr = {
                "Ouvert": kpis["by_status"].get("open", 0),
                "Ferme bientôt (≤14j)": kpis["by_status"].get("urgent", 0),
                "À surveiller": kpis["by_status"].get("watch", 0),
                "Fermé": kpis["by_status"].get("closed", 0),
            }
            st.bar_chart(status_fr, color="#FF5A1F")

    # Bandeau d'honnêteté sur les données
    verified_total = sum(1 for p in programs if getattr(p, "verified", False))
    unverified_total = len(programs) - verified_total
    st.markdown(
        f"""
        <div class="honesty-box">
            <strong>🛡️ Transparence des données :</strong> Ce radar repose sur un dataset curé manuellement ({len(programs)} programmes, aucun scraping).
            <strong>{verified_total}</strong> programme(s) sont confirmés pour le cycle en cours et <strong>{unverified_total}</strong> sont étiquetés
            <em>« à vérifier sur la page officielle »</em>. Vérifie toujours les dates sur le portail de l'employeur.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # FILTRES EN SIDEBAR (conservation de tous les filtres existants)
    # -----------------------------------------------------------------------
    st.sidebar.header("🔎 Filtres de recherche")

    all_sessions = sorted({s for p in programs for s in (getattr(p, "sessions", []) or [])})
    all_categories = sorted({str(getattr(p, "category", "")) for p in programs if getattr(p, "category", "")})
    all_locations = sorted({loc for p in programs for loc in (getattr(p, "locations", []) or [])})

    search_query = st.sidebar.text_input("Recherche (entreprise, mot-clé)", value="")
    selected_session = st.sidebar.selectbox("Session", ["Toutes"] + all_sessions)
    selected_category = st.sidebar.selectbox("Catégorie", ["Toutes"] + all_categories)
    selected_location = st.sidebar.selectbox("Lieu", ["Tous"] + all_locations)

    only_paid = st.sidebar.checkbox("Rémunéré uniquement", value=False)
    only_eligible = st.sidebar.checkbox("Admissible uniquement", value=False)
    only_first_year = st.sidebar.checkbox("Ouvert aux 1re année (min_year ≤ 1)", value=False)

    # Filtrage des programmes
    filtered_programs: List[tuple[Any, Any]] = []
    for prog in programs:
        bd = explain_score(profile, prog)

        if selected_session != "Toutes" and selected_session not in (getattr(prog, "sessions", []) or []):
            continue
        if selected_category != "Toutes" and str(getattr(prog, "category", "")) != selected_category:
            continue
        if selected_location != "Tous" and selected_location not in (getattr(prog, "locations", []) or []):
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

    # Tri par score décroissant puis par nom d'entreprise
    filtered_programs.sort(key=lambda item: (-item[1].total, str(getattr(item[0], "firm", ""))))

    # -----------------------------------------------------------------------
    # NAVIGATION PAR ONGLETS : PROGRAMMES / CE QUI TE BLOQUE / SUIVI SQLITE
    # -----------------------------------------------------------------------
    tracked_map = get_all_tracked()

    tab_all, tab_blockers, tab_tracker = st.tabs([
        f"🎯 Programmes & Scores ({len(filtered_programs)})",
        "🚧 Ce qui te bloque (Plan d'action)",
        f"📋 Suivi de candidatures ({len(tracked_map)})",
    ])

    # --- ONGLET 1 : PROGRAMMES & SCORE EXPLIQUÉ ---
    with tab_all:
        if not filtered_programs:
            st.warning("Aucun programme ne correspond aux filtres sélectionnés.")
        for prog, bd in filtered_programs:
            pid = str(getattr(prog, "id", f"{getattr(prog, 'firm', '')}-{getattr(prog, 'program', '')}"))
            firm = str(getattr(prog, "firm", ""))
            title = str(getattr(prog, "program", ""))
            category = str(getattr(prog, "category", ""))
            locs = ", ".join(getattr(prog, "locations", []) or [])
            is_verified = bool(getattr(prog, "verified", False))

            st_code = _safe_deadline_status(prog, today)
            d_left = _safe_days_until(prog, today)

            badge_html = _status_badge_html(st_code, d_left)
            verif_html = (
                '<span class="badge badge-verified">✓ Vérifié</span>'
                if is_verified
                else '<span class="badge badge-unverified">⚠️ À vérifier sur la page officielle</span>'
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

            with st.expander(f"Détails du score, admissibilité & suivi — {firm} ({title})"):
                c_left, c_right = st.columns([3, 2])
                with c_left:
                    if bd.eligible:
                        st.markdown("#### ✅ Admissible — Décomposition du score")
                        st.progress(bd.total / 100.0)
                        st.markdown(
                            f"- **Admissibilité validée :** `+{bd.base_points} pts`\n"
                            f"- **Intérêts partagés ({len(bd.shared_interests)}) :** `+{bd.interest_points} pts` "
                            f"{'(' + ', '.join(bd.shared_interests) + ')' if bd.shared_interests else '(aucun tag commun)'}\n"
                            f"- **Ville cible ({ getattr(profile, 'home_base', '') }) :** `+{bd.location_points} pts`\n"
                            f"- **Stage rémunéré :** `+{bd.paid_points} pts`\n"
                            f"- **Total :** **{bd.total} / 100**"
                        )
                    else:
                        st.markdown("#### ❌ Non admissible (Score : 0 / 100)")
                        for r in bd.reasons:
                            st.error(f"• {r}")
                        st.info(f"💡 **Action recommandée :** {bd.action_hint}")

                    dl_val = getattr(prog, "deadline", None) or "Non spécifiée"
                    dl_note = getattr(prog, "deadline_note", None) or ""
                    notes_txt = getattr(prog, "notes", None) or ""
                    st.markdown(f"**Date limite :** `{dl_val}` {f'— *{dl_note}*' if dl_note else ''}")
                    if notes_txt:
                        st.caption(f"Note : {notes_txt}")

                    apply_url = getattr(prog, "apply_url", None)
                    if apply_url:
                        st.link_button("🌐 Ouvrir la page officielle de candidature", str(apply_url))

                with c_right:
                    st.markdown("#### 📌 Suivre cette candidature")
                    current_track = tracked_map.get(pid, {"status": "Non suivi", "notes": ""})
                    cur_status = current_track["status"] if current_track["status"] in VALID_STATUSES else "Non suivi"

                    new_status = st.selectbox(
                        "Statut",
                        VALID_STATUSES,
                        index=VALID_STATUSES.index(cur_status),
                        key=f"status_{pid}",
                    )
                    new_note = st.text_input(
                        "Note personnelle",
                        value=current_track.get("notes", ""),
                        placeholder="Ex: Référé par un alumnus, CV envoyé...",
                        key=f"note_{pid}",
                    )
                    if st.button("💾 Enregistrer le suivi", key=f"save_{pid}", use_container_width=True):
                        set_application_status(pid, new_status, new_note)
                        st.success("Suivi mis à jour dans SQLite !")
                        st.rerun()

    # --- ONGLET 2 : VUE « CE QUI TE BLOQUE » ---
    with tab_blockers:
        st.subheader("🚧 Programmes actuellement inaccessibles — et comment les débloquer")
        st.caption(
            "Un « non » aujourd'hui prépare ta stratégie de l'an prochain. Voici pourquoi ces programmes te bloquent et l'action concrète associée."
        )

        ineligible_list = [(p, explain_score(profile, p)) for p in programs]
        ineligible_list = [(p, b) for p, b in ineligible_list if not b.eligible]

        if not ineligible_list:
            st.success("🎉 Félicitations ! Tu es admissible à l'intégralité des programmes du radar.")
        else:
            for prog, bd in ineligible_list:
                firm = str(getattr(prog, "firm", ""))
                title = str(getattr(prog, "program", ""))
                reasons_str = " ; ".join(bd.reasons)
                with st.container(border=True):
                    b_col1, b_col2 = st.columns([3, 2])
                    with b_col1:
                        st.markdown(f"**{firm} — {title}**")
                        st.markdown(f"🔴 **Raison(s) du blocage :** {reasons_str}")
                    with b_col2:
                        st.markdown(f"🎯 **Action concrète :**\n\n`{bd.action_hint}`")

    # --- ONGLET 3 : SUIVI DE CANDIDATURES (SQLITE + EXPORT CSV) ---
    with tab_tracker:
        st.subheader("📋 Mes candidatures suivies (Base SQLite locale)")
        csv_data = export_tracked_to_csv(programs)

        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.caption("Les statuts sont sauvegardés localement via `sqlite3` sans jamais modifier `data/programs.yaml`.")
        with t_col2:
            st.download_button(
                label="📥 Exporter en CSV",
                data=csv_data.encode("utf-8"),
                file_name=f"radar_candidatures_{today.isoformat()}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        active_tracked = {
            k: v for k, v in tracked_map.items() if v["status"] != "Non suivi" or v["notes"].strip()
        }

        if not active_tracked:
            st.info("Tu n'as encore suivi aucun programme. Ouvre les détails d'un programme dans le premier onglet pour lui attribuer un statut (À postuler, Postulé, Entretien, Offre, Refusé).")
        else:
            prog_by_id = {str(getattr(p, "id", "")): p for p in programs}
            rows_display = []
            for pid, info in active_tracked.items():
                p_obj = prog_by_id.get(pid)
                rows_display.append({
                    "Entreprise": getattr(p_obj, "firm", pid) if p_obj else pid,
                    "Programme": getattr(p_obj, "program", "") if p_obj else "",
                    "Statut": info["status"],
                    "Notes": info["notes"],
                    "Mise à jour (UTC)": info["updated_at"],
                })
            st.dataframe(rows_display, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()