import type { Interest, Profile, Program } from "./types";

export type Bilingual = { fr: string; en: string };

export const DEFAULT_PROFILE: Profile = {
  year: 1, school: "HEC Montréal", grad: "2029-05", city: "Montréal", usAuth: false,
  interests: ["quant", "markets", "investment_banking", "corporate_finance"],
};

const frOrd = (n: number) => (n === 1 ? "1re" : `${n}e`);

export function eligibility(p: Program, prof: Profile): { eligible: boolean; reasons: Bilingual[] } {
  const reasons: Bilingual[] = [];
  const a = prof.year;
  if (p.min_year != null && a < p.min_year)
    reasons.push({ fr: `demande la ${frOrd(p.min_year)} année minimum (profil : ${frOrd(a)} année)`, en: `requires year ${p.min_year} minimum (profile: year ${a})` });
  if (p.max_year != null && a > p.max_year)
    reasons.push({ fr: `réservé jusqu'à la ${frOrd(p.max_year)} année (profil : ${frOrd(a)} année)`, en: `only up to year ${p.max_year} (profile: year ${a})` });
  if (p.grad_not_before && prof.grad < p.grad_not_before)
    reasons.push({ fr: `demande une diplomation à partir de ${p.grad_not_before} (diplomation du profil : ${prof.grad})`, en: `requires graduation on or after ${p.grad_not_before} (profile graduation: ${prof.grad})` });
  if (p.grad_window) {
    const [s, e] = p.grad_window;
    if (prof.grad < s || prof.grad > e)
      reasons.push({ fr: `demande une diplomation entre ${s} et ${e} (diplomation du profil : ${prof.grad})`, en: `requires graduation between ${s} and ${e} (profile graduation: ${prof.grad})` });
  }
  if (p.requires_us_auth && !prof.usAuth)
    reasons.push({ fr: "exige une autorisation de travail aux États-Unis", en: "requires US work authorization" });
  return { eligible: reasons.length === 0, reasons };
}

export interface ScoreBreakdown { eligibility: number; interests: number; city: number; paid: number; total: number }

export function breakdown(p: Program, prof: Profile): ScoreBreakdown {
  if (!eligibility(p, prof).eligible) return { eligibility: 0, interests: 0, city: 0, paid: 0, total: 0 };
  const shared = p.interests.filter((i: Interest) => prof.interests.includes(i)).length;
  const interests = p.interests.length ? Math.round((30 * shared) / p.interests.length) : 0;
  const city = p.locations.includes(prof.city) ? 10 : 0;
  const paid = p.paid === true ? 10 : 0;
  return { eligibility: 50, interests, city, paid, total: Math.min(100, 50 + interests + city + paid) };
}

export const score = (p: Program, prof: Profile) => breakdown(p, prof).total;

export interface Ranked { program: Program; score: number; eligible: boolean; reasons: Bilingual[]; breakdown: ScoreBreakdown }

export function rank(programs: Program[], prof: Profile): Ranked[] {
  return programs
    .map((program) => {
      const el = eligibility(program, prof);
      const b = breakdown(program, prof);
      return { program, score: b.total, eligible: el.eligible, reasons: el.reasons, breakdown: b };
    })
    .sort((x, y) =>
      Number(y.eligible) - Number(x.eligible) || y.score - x.score || x.program.firm.localeCompare(y.program.firm, "fr"),
    );
}

/** Days until deadline (negative = passed), null when no published deadline. */
export function daysLeft(deadline: string | null, today: Date = new Date()): number | null {
  if (!deadline) return null;
  const [y = 0, m = 1, d = 1] = deadline.split("-").map(Number);
  const t = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((Date.UTC(y, m - 1, d) - t) / 86400000);
}
export const isClosed = (p: Program, today?: Date) => { const d = daysLeft(p.deadline, today); return d != null && d < 0; };

/** Display order: keeps rank order but moves closed programs to the bottom (never removed). */
export function closedLast(list: Ranked[], today?: Date): Ranked[] {
  return [...list.filter((r) => !isClosed(r.program, today)), ...list.filter((r) => isClosed(r.program, today))];
}
