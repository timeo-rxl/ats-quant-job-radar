import { langStore, type Lang } from "./store";
import type { Category, Interest, Session } from "./types";

const dict = {
  fr: {
    tagline: "31 stages. Zéro bruit. Un seul match.",
    nav_home: "Accueil", nav_find: "Trouve ton stage", nav_explore: "Explorer", nav_track: "Suivi",
    footer: "Données vérifiées sur les pages officielles — une deadline n'est jamais devinée.",
    hero_kicker: "Radar de stages · finance · quant · tech",
    hero_sub: "Pour étudiants de 1re et 2e année. 31 programmes réels, filtrés selon ton année, ta diplomation, ta ville et ton autorisation de travail. Un score de 0 à 100 que tu peux lire ligne par ligne.",
    cta_find: "Lancer le scan", cta_explore: "Voir les 31 programmes",
    strip_label: "PASSE TA SOURIS — 26 EMPLOYEURS, 31 PROGRAMMES",
    kpi_programs: "programmes", kpi_eligible: "admissibles pour ton profil", kpi_next: "prochaine deadline", kpi_mtl: "à Montréal",
    top_title: "Tes 3 meilleurs signaux", top_sub: "Profil actuel", how_title: "Comment ça marche",
    how1_t: "Décris ton profil", how1_d: "Année, diplomation, intérêts, ville, autorisation US. Cinq questions, aucun compte.",
    how2_t: "Lis ton score", how2_d: "Éligibilité 50 + intérêts 30 + ville 10 + rémunéré 10. Inadmissible = 0, avec la raison exacte.",
    how3_t: "Postule à la source", how3_d: "Chaque programme renvoie vers sa page officielle. Suis tes candidatures en local.",
    verified: "VÉRIFIÉ", to_verify: "À VÉRIFIER", closed: "Fermé", apply: "Postuler", details: "Fiche",
    no_deadline: "Pas de deadline publiée — postule vite", score: "Score", ineligible: "Inadmissible",
    paid: "Rémunéré", unpaid: "Non rémunéré", paid_unknown: "Rémunération inconnue",
    step: "Étape", of: "sur", next: "Suivant", back: "Retour", see_results: "Voir mon classement", restart: "Refaire le scan",
    q_year: "En quelle année d'études es-tu ?", q_grad: "Quand obtiens-tu ton diplôme ?", q_interests: "Qu'est-ce qui t'intéresse ?",
    q_city: "Ta ville principale ?", q_us: "As-tu une autorisation de travail aux États-Unis ?",
    year_n: (n: number) => (n === 1 ? "1re année" : `${n}e année`), yes: "Oui", no: "Non",
    results: "Ton classement", blockers: "Ce qui te bloque", blockers_none: "Rien ne te bloque. Rare.",
    bd_elig: "Éligibilité", bd_int: "Intérêts", bd_city: "Ville", bd_paid: "Rémunéré",
    reset_profile: "Réinitialiser le profil", grad_format: "AAAA-MM", grad_calendar: "Choisir le mois de diplomation",
    filters: "Filtres", f_category: "Catégorie", f_session: "Session", f_city: "Ville", f_paid: "Rémunéré seulement",
    f_eligible: "Admissibles seulement", f_search: "Entreprise, programme, tag…", all: "Tous", reset: "Réinitialiser",
    results_count: (n: number) => `${n} programme${n > 1 ? "s" : ""}`, firm_filter: "Entreprise",
    who: "Qui peut postuler", min_year: "Année min.", max_year: "Année max.", grad: "Diplomation", us_auth: "Autorisation US",
    required: "Requise", not_required: "Non requise", none: "—", from: "à partir de", between: "entre", and: "et",
    interests: "Intérêts", deadline: "Deadline", status: "Vérification", verified_on: "vérifié le", notes: "Notes importantes",
    official: "Lien officiel", mark_applied: "Marquer comme postulé", in_tracker: "Dans ton suivi", eligibility_you: "Pour ton profil",
    track_title: "Suivi des candidatures", track_empty: "Aucune candidature suivie. Marque un programme depuis sa fiche ou Explorer.",
    export_csv: "Exporter CSV", remove: "Retirer", updated: "Mis à jour", locations: "Villes", sessions: "Sessions",
    st_todo: "À postuler", st_applied: "Postulé", st_interview: "Entretien", st_offer: "Offre", st_rejected: "Refusé",
    add_track: "Suivre", not_found: "Programme introuvable", days: (n: number) => `J-${n}`, today: "Aujourd'hui",
  },
  en: {
    tagline: "31 internships. Zero noise. One match.",
    nav_home: "Home", nav_find: "Find your internship", nav_explore: "Explore", nav_track: "Tracker",
    footer: "Data verified on official pages — a deadline is never guessed.",
    hero_kicker: "Internship radar · finance · quant · tech",
    hero_sub: "For 1st and 2nd year students. 31 real programs, filtered by your year, graduation date, city and work authorization. A 0–100 score you can read line by line.",
    cta_find: "Start the scan", cta_explore: "See all 31 programs",
    strip_label: "MOVE YOUR MOUSE — 26 EMPLOYERS, 31 PROGRAMS",
    kpi_programs: "programs", kpi_eligible: "eligible for your profile", kpi_next: "next deadline", kpi_mtl: "in Montréal",
    top_title: "Your top 3 signals", top_sub: "Current profile", how_title: "How it works",
    how1_t: "Describe your profile", how1_d: "Year, graduation, interests, city, US authorization. Five questions, no account.",
    how2_t: "Read your score", how2_d: "Eligibility 50 + interests 30 + city 10 + paid 10. Ineligible = 0, with the exact reason.",
    how3_t: "Apply at the source", how3_d: "Every program links to its official page. Track applications locally.",
    verified: "VERIFIED", to_verify: "TO VERIFY", closed: "Closed", apply: "Apply", details: "Details",
    no_deadline: "No published deadline — apply fast", score: "Score", ineligible: "Ineligible",
    paid: "Paid", unpaid: "Unpaid", paid_unknown: "Pay unknown",
    step: "Step", of: "of", next: "Next", back: "Back", see_results: "See my ranking", restart: "Rerun the scan",
    q_year: "What year of study are you in?", q_grad: "When do you graduate?", q_interests: "What are you into?",
    q_city: "Your main city?", q_us: "Do you have US work authorization?",
    year_n: (n: number) => `Year ${n}`, yes: "Yes", no: "No",
    results: "Your ranking", blockers: "What's blocking you", blockers_none: "Nothing blocks you. Rare.",
    bd_elig: "Eligibility", bd_int: "Interests", bd_city: "City", bd_paid: "Paid",
    reset_profile: "Reset profile", grad_format: "YYYY-MM", grad_calendar: "Choose graduation month",
    filters: "Filters", f_category: "Category", f_session: "Session", f_city: "City", f_paid: "Paid only",
    f_eligible: "Eligible only", f_search: "Company, program, tag…", all: "All", reset: "Reset",
    results_count: (n: number) => `${n} program${n > 1 ? "s" : ""}`, firm_filter: "Company",
    who: "Who can apply", min_year: "Min. year", max_year: "Max. year", grad: "Graduation", us_auth: "US authorization",
    required: "Required", not_required: "Not required", none: "—", from: "on or after", between: "between", and: "and",
    interests: "Interests", deadline: "Deadline", status: "Verification", verified_on: "verified on", notes: "Important notes",
    official: "Official link", mark_applied: "Mark as applied", in_tracker: "In your tracker", eligibility_you: "For your profile",
    track_title: "Application tracker", track_empty: "No tracked applications. Mark a program from its page or Explore.",
    export_csv: "Export CSV", remove: "Remove", updated: "Updated", locations: "Cities", sessions: "Sessions",
    st_todo: "To apply", st_applied: "Applied", st_interview: "Interview", st_offer: "Offer", st_rejected: "Rejected",
    add_track: "Track", not_found: "Program not found", days: (n: number) => `D-${n}`, today: "Today",
  },
} as const;

export type Dict = (typeof dict)["fr"];

export const INTEREST_LABELS: Record<Interest, [string, string]> = {
  quant: ["Quant & Recherche quantitative", "Quant & Quantitative Research"],
  markets: ["Marchés financiers (Sales & Trading)", "Financial Markets (Sales & Trading)"],
  investment_banking: ["Banque d'investissement (M&A / ECM / DCM)", "Investment Banking (M&A / ECM / DCM)"],
  asset_management: ["Gestion d'actifs & Portefeuille", "Asset & Portfolio Management"],
  fintech: ["Fintech & Paiements", "Fintech & Payments"],
  venture_capital: ["Capital de risque (VC)", "Venture Capital (VC)"],
  ai: ["Intelligence artificielle & Data", "Artificial Intelligence & Data"],
  startups: ["Startups & Produit", "Startups & Product"],
  corporate_finance: ["Finance d'entreprise & Crédit", "Corporate Finance & Credit"],
  tech: ["Tech & Génie logiciel", "Tech & Software Engineering"],
};
export const CATEGORY_LABELS: Record<Category, [string, string]> = {
  banking: ["Banque", "Banking"], quant: ["Quant", "Quant"], tech: ["Tech", "Tech"],
  vc_startup: ["VC & startups", "VC & Startups"], public: ["Public", "Public"],
};
export const SESSION_LABELS: Record<Session, [string, string]> = {
  summer_2027: ["Été 2027", "Summer 2027"], winter_2027: ["Hiver 2027", "Winter 2027"],
  fall_2027: ["Automne 2027", "Fall 2027"], school_year: ["Année scolaire", "School year"],
  summer_2028: ["Été 2028", "Summer 2028"],
};

export function useI18n() {
  const lang = langStore.use();
  const i = lang === "fr" ? 0 : 1;
  return {
    lang, t: dict[lang] as Dict, setLang: (l: Lang) => langStore.set(l),
    interest: (k: Interest) => INTEREST_LABELS[k][i],
    category: (k: Category) => CATEGORY_LABELS[k][i],
    session: (k: Session) => SESSION_LABELS[k][i],
  };
}
