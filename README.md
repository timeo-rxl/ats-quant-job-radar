# ats-quant-job-radar

**Internship radar for a first-year student in finance, quant and tech.**
31 programmes, one profile, one honest answer per programme: eligible,
when it closes, and why not if not.

No scraping. The dataset is curated from real research, every link
points to the official application page, and anything unverified is
labelled as such.

**Live demo:** https://timeo-rxl-ats-quant-job-radar-app-q25tit.streamlit.app

## En français, en 30 secondes

On décrit un profil une fois (`my_profile.yaml`) : année d'études, date
de diplomation, autorisation de travail aux États-Unis, centres d'intérêt.
Le radar indique, pour chaque programme :

- **✅ Admissible** — avec un score /100 et la date limite.
- **❌ Pas admissible (encore)** — avec la raison exacte : « demande une
  diplomation entre déc. 2027 et juin 2028 », « exige une autorisation
  de travail aux États-Unis », « demande la 2e année minimum ».
- **⏰ Échéances** — ouvert, ferme bientôt (≤ 14 jours), fermé, à surveiller.

Filtres disponibles : session (été 2027, hiver, été 2028…), catégorie
(banque, quant, tech, VC/startup, public), lieu, et recherche par
mot-clé. Quand l'étudiant passe en 2e année, il change un chiffre dans
son profil et tout le radar se recalcule.

## v2.0 — what changed (10 Nov 2026)

The demo is now a full interactive app, not just filters:

- **🎯 Radar onboarding** — a rule-based chat assistant (no API key,
  no LLM call) asks 5 questions (year, graduation, interests, city,
  US work authorisation) and builds *the visitor's* profile, then
  shows *their* matches. The example profile is still one click away.
- **📊 KPI dashboard** — eligible / total, deadlines in the next
  30 days, next-deadline countdown, Montréal count, charts by category
  and deadline status.
- **🔍 Score explained** — every score is broken down (50 eligibility
  + up to 30 interests + 10 home city + 10 paid) so the visitor sees
  *why* a programme ranks first.
- **🚧 "Ce qui te bloque"** — every ineligible programme lists the
  exact reason plus one concrete action ("Re-postule en 2e année",
  "Il te faudra une autorisation US").
- **📋 Application tracker** — mark each programme À postuler /
  Postulé / Entretien / Offre / Refusé with a note, stored in a local
  SQLite database (`radar_tracker.db`, git-ignored, never the dataset),
  exportable to CSV.
- **New design** — navy `#0B1B33` / orange `#FF5A1F` cards, hero,
  status badges. Same honest data: 2 programmes verified, 29 to verify.

## What it does

| Module | Question it answers |
| --- | --- |
| `radar/matching.py` | Am I eligible? Why (not)? Score /100, explainable |
| `radar/timeline.py` | Open, closing soon, closed, or watch? How many days left? |
| `radar/data.py` | Load the programme dataset and the student profile from YAML |
| `radar/scoring.py` | Why this score? KPI dashboard, blockers with actions |
| `radar/onboarding.py` | 5-question chat that builds a visitor's profile |
| `radar/tracker.py` | Application tracking in SQLite + CSV export |
| `demo.py` | CLI — the radar, the deadlines, the rejections with reasons |
| `app.py` | Streamlit demo — the same radar as a small filterable site |

## Try it

```bash
pip install -r requirements.txt

python demo.py                              # the radar for the example profile, today
python demo.py --date 2027-01-15           # the radar, on another date
streamlit run app.py                        # the filterable site

python -m pytest tests/ -q    # 28 tests (17 original + 11 for v2)
```

## Example profile

`my_profile.yaml` — a first-year B.A.A. student at HEC Montréal,
graduating 2029-05, no US work authorisation, Montréal-based, open
to remote. Interests: quant, markets, investment banking, asset
management, fintech, venture capital, AI, startups, corporate finance.

Change `current_year` to 2 next year and re-run: the sophomore
programmes (Morgan Stanley Early Insights, CPP Discover…) flip to
eligible automatically.

## Worked example — first-year profile (10 Nov 2026)

**Top matches (score 100/100) :** BNP Paribas — Corporate Credit
Analyst Summer 2027 (Montréal) and Banque Nationale — Corporate
Finance Internships (Montréal). Both in Montréal, both open to
first-years — verify they are still open on the official page.

**16 programmes eligible, 15 not — and the rejections are the point :**
the big-bank markets/IB roles (RBC, TD, BMO, Goldman Summer Analyst)
require graduation Dec 2027 / 2028, so they are sophomore-year
targets, not first-year ones. The US programmes (JPMorgan Emerging
Talent, Jane Street FOCUS, Citadel Discover) require US work
authorisation. The radar tells you this instead of letting you apply
into a wall.

**Deadlines already gone for summer 2027 :** Next 36 (14 Oct 2026),
BMO (30 Oct 2026). Still open : Kleiner Perkins Fellows (31 Jan 2027).
To watch : Bank of Canada (applications in January 2027), Front Row
Ventures (January cycles), Wealthsimple summer postings (Jan–Apr 2027).

## Project structure

```
ats-quant-job-radar/
├── radar/
│   ├── models.py       # Profile, InternshipProgram — plain dataclasses
│   ├── matching.py     # eligibility + reasons, score, filters, ranking
│   ├── timeline.py     # deadline statuses, days left, upcoming list
│   ├── data.py         # YAML loading
│   ├── scoring.py      # score breakdown, KPIs, blocker actions (v2)
│   ├── onboarding.py   # 5-question chat, visitor profile (v2)
│   └── tracker.py      # SQLite application tracking + CSV export (v2)
├── data/
│   └── programs.yaml   # 31 programmes, sources + verification status
├── my_profile.yaml     # the student — edit this, the radar follows
├── demo.py             # CLI
├── app.py              # Streamlit demo
└── tests/
    ├── test_radar.py        # 17 tests, fixed reference date
    └── test_v2_features.py  # 11 tests for scoring, onboarding, tracker
```

## Honesty notes

- **Curated, not scraped.** Job boards change their pages and their
  rules; scraping them breaks and can violate their terms. This radar
  stores facts and links out — you apply on the official page.
- **2 programmes verified, 29 to verify.** The verified ones were
  checked against their source on 13 Oct 2026. The rest are known
  programmes whose details must be confirmed on the official page
  before applying — deadlines move every year, and an expired posting
  is worse than no posting.
- **The dataset is a snapshot, not a live feed.** Add a programme by
  adding ~15 lines to `data/programs.yaml`; remove one by deleting
  them. If a deadline passes, the radar says "fermé" instead of
  pretending the opportunity is still there.
- **Not a guarantee.** A score of 100 means "eligible on paper and
  matching your interests", not "you will get the offer".
