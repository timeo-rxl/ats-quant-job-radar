# StageScope — Ton radar de stages. Zéro bruit. Un seul match.

**Live demo:** https://stagescope.lovable.app

StageScope (formerly ATS Quant Job Radar) is an internship radar for 1st/2nd-year students in finance, quant and tech. It filters 31 real programmes (banks, quant, tech, VC, public sector) against your profile — study year, graduation date, city, US work authorization, interests — and scores each programme 0–100 with an explainable breakdown. No scraping: every programme links to its official application page, and a deadline is never guessed.

## The signature interaction

The home page has an interactive dotted band: move your mouse across it and employer logo cards appear at your cursor, fanned out like a hand of cards, then fade away. Click a card to open the Explorer filtered by that employer. On touch devices the band plays by itself.

## How the matching works

The engine lives in `src/lib/matching.ts` (tests in `src/lib/matching.test.ts`):

| Rule | How it works |
| --- | --- |
| **Eligibility checklist** | min/max study year, graduation not before / graduation window, US work authorization — every refusal carries its reason in plain language (FR + EN) |
| **Score 0–100** | 0 if ineligible. Otherwise 50 for being eligible + up to 30 for shared interests + 10 for home city + 10 if paid, capped at 100 |
| **Ranking** | Eligible first, best score first, then alphabetical by firm |
| **Closed deadlines** | A programme whose deadline has passed shows as closed and moves to the bottom of lists — never deleted |

With the default profile (1st year, HEC Montréal, graduation 2029-05, Montréal, no US authorization, interests quant / markets / investment banking / corporate finance): BNP Paribas Corporate Credit Analyst 100, Banque Nationale Corporate Finance 100, Desjardins 85, Banque du Canada 80, Capital One Strategy Analyst 70.

## Pages

**Accueil** (hero, logo band, live KPIs, top matches), **Trouve ton stage** (5-step onboarding → personalized ranking + "Ce qui te bloque"), **Explorer** (filters: category, session, city, paid only, eligible only, text search), **programme detail** (eligibility, deadline with [VÉRIFIÉ] / [À VÉRIFIER] badge, official link), **Suivi** (application tracker in localStorage + CSV export).

French by default, with a FR/EN toggle. No backend, no account: profile, language and tracker live in localStorage.

## Try it

```bash
npm install
npm run dev     # local dev server
npm test        # vitest — matching engine + routing
npm run build   # production build
```

## Data — read this

The dataset (`src/data/programs.json`, 31 programmes) is curated from official pages only. `verified: true` means checked against the source on the shown date; `verified: false` means known programme, details to verify on the official page before applying. Only deadlines published on an official page are listed — the rest show their note or "no published deadline". Deadlines move every year: the official page decides, never this repo.

## Tech

React + Vite + Tailwind CSS + shadcn/ui + TanStack Router. Built on Lovable (November 2026).

## History

The matching engine was first built and tested in Python (38 tests) with a Streamlit demo; the full history is in the git log. The current app is a complete rebuild (Lovable, November 2026) that ports the engine to TypeScript and ships it as a real product interface, under the new name StageScope.
