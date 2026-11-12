import { describe, expect, it } from "vitest";
import { PROGRAMS } from "./programs";
import { DEFAULT_PROFILE, eligibility, score, rank, daysLeft } from "./matching";

const P = (id: string) => PROGRAMS.find((p) => p.id === id)!;

describe("matching", () => {
  it("dataset has 31 programs", () => expect(PROGRAMS).toHaveLength(31));

  it("default profile: BNP Corporate Credit and BNC Corporate Finance score 100", () => {
    expect(score(P("bnp-corporate-credit"), DEFAULT_PROFILE)).toBe(100);
    expect(score(P("bnc-corporate-finance"), DEFAULT_PROFILE)).toBe(100);
  });

  // Spec formula: 50 + round(30*2/3)=20 + 0 city (Ottawa) + 10 paid = 80
  it("default profile: Banque du Canada = 80 per the immutable formula", () => {
    expect(score(P("bank-of-canada"), DEFAULT_PROFILE)).toBe(80);
  });
  // Spec formula: 50 + round(30*1/3)=10 + 0 city (Toronto) + 10 paid = 70
  it("default profile: Capital One Strategy = 70 per the immutable formula", () => {
    expect(score(P("capital-one-strategy"), DEFAULT_PROFILE)).toBe(70);
  });

  it("graduating 2027-05 is ineligible for Capital One (needs 2027-12+)", () => {
    const r = eligibility(P("capital-one-strategy"), { ...DEFAULT_PROFILE, grad: "2027-05" });
    expect(r.eligible).toBe(false);
    expect(r.reasons[0]?.fr).toBe("demande une diplomation à partir de 2027-12 (diplomation du profil : 2027-05)");
  });

  it("max_year 1 refuses a 2nd-year profile (Jane Street FOCUS)", () => {
    const r = eligibility(P("janestreet-focus"), { ...DEFAULT_PROFILE, year: 2 });
    expect(r.eligible).toBe(false);
    expect(r.reasons[0]?.fr).toBe("réservé jusqu'à la 1re année (profil : 2e année)");
  });

  it("score is 0 when ineligible even with all interests shared", () => {
    const p = P("goldman-summer-analyst");
    expect(score(p, { ...DEFAULT_PROFILE, interests: [...p.interests] })).toBe(0);
  });

  it("ranking puts eligible first, then score, then firm", () => {
    const r = rank(PROGRAMS, DEFAULT_PROFILE);
    expect(r.slice(0, 2).map((x) => x.program.id)).toEqual(["bnc-corporate-finance", "bnp-corporate-credit"]);
    const firstIneligible = r.findIndex((x) => !x.eligible);
    expect(r.slice(firstIneligible).every((x) => !x.eligible)).toBe(true);
  });

  it("daysLeft counts from today", () => {
    expect(daysLeft("2026-12-06", new Date(2026, 10, 12))).toBe(24);
    expect(daysLeft(null)).toBeNull();
  });
});
