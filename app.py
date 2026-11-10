"""Streamlit demo — le radar en petit site avec filtres.

    streamlit run app.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from radar import (
    STATUS_FR,
    days_until,
    deadline_status,
    eligibility,
    load_profile,
    load_programs,
    match_score,
    rank_for_profile,
)

BASE = Path(__file__).resolve().parent


@st.cache_data
def _load():
    return load_profile(BASE / "my_profile.yaml"), load_programs(BASE / "data/programs.yaml")


profile, programs = _load()
today = date.today()

st.set_page_config(page_title="ATS Quant Job Radar", layout="wide")
st.title("🎯 ATS Quant Job Radar")
st.caption(
    f"Profil d'exemple : {profile.name} — {profile.school}, {profile.current_year}re année, "
    f"diplomation {profile.graduation_ym}. Données vérifiées ou étiquetées à vérifier — "
    "aucun scraping, liens vers les pages officielles."
)

with st.sidebar:
    st.header("Filtres")
    session = st.selectbox(
        "Session",
        ["Toutes", "summer_2027", "winter_2027", "fall_2027", "school_year", "summer_2028"],
    )
    category = st.selectbox(
        "Catégorie", ["Toutes", "banking", "quant", "tech", "vc_startup", "public"]
    )
    location = st.selectbox(
        "Lieu",
        ["Tous", "Montréal", "Toronto", "Vancouver", "New York", "Chicago", "Ottawa", "Canada"],
    )
    paid_only = st.checkbox("Rémunérés seulement")
    eligible_only = st.checkbox("Admissible pour ce profil", value=True)
    first_year_only = st.checkbox("Ouverts aux 1res années")
    query = st.text_input("Recherche (firme, programme, mot-clé)")

ranked = {p.id: s for p, s in rank_for_profile(programs, profile)}

shown = []
for p in programs:
    if session != "Toutes" and session not in p.sessions:
        continue
    if category != "Toutes" and p.category != category:
        continue
    if location != "Tous" and location not in p.locations:
        continue
    if paid_only and p.paid is not True:
        continue
    if eligible_only and p.id not in ranked:
        continue
    if first_year_only and p.min_year is not None and p.min_year > 1:
        continue
    if query and query.lower() not in f"{p.firm} {p.program} {p.category}".lower():
        continue
    shown.append(p)

shown.sort(key=lambda p: (-ranked.get(p.id, 0), p.firm))
st.subheader(f"{len(shown)} programme(s)")

for p in shown:
    ok, reasons = eligibility(profile, p)
    status = deadline_status(p, today)
    score = ranked.get(p.id, 0)
    title = f"{p.label}  ·  score {score}/100  ·  {STATUS_FR[status]}"
    if status in ("open", "urgent") and p.deadline:
        title += f" ({days_until(p, today)} j)"
    with st.expander(title):
        st.write(f"**Type :** {p.type} · **Catégorie :** {p.category}")
        st.write(f"**Lieux :** {', '.join(p.locations)} · **Rémunéré :** "
                 f"{'oui' if p.paid else ('non' if p.paid is False else 'inconnu')}")
        st.write(f"**Sessions :** {', '.join(p.sessions)}")
        if p.deadline:
            st.write(f"**Date limite :** {p.deadline}")
        if p.deadline_note:
            st.write(f"**Calendrier :** {p.deadline_note}")
        if ok:
            st.success("Admissible pour ce profil.")
        else:
            st.warning("Pas admissible : " + "; ".join(reasons))
        if p.notes:
            st.write(p.notes)
        if not p.verified:
            st.warning("⚠️ Détails à vérifier sur la page officielle avant de postuler.")
        if p.apply_url:
            st.link_button("Postuler / page officielle", p.apply_url)
        elif p.search_hint:
            st.write(f"Rechercher sur le site officiel : **{p.search_hint}**")
