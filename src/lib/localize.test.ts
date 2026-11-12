import { describe, expect, it } from "vitest";
import { PROGRAMS } from "./programs";
import { programDeadlineNote, programNotes, cityLabel } from "./localize";

const P = (id: string) => PROGRAMS.find((p) => p.id === id)!;

describe("EN localization", () => {
  it("BNP Paribas notes and deadline note show in English", () => {
    expect(programNotes(P("bnp-corporate-credit"), "en")).toMatch(/^Summer 2027 internship in Montréal/);
    expect(programDeadlineNote(P("bnp-corporate-credit"), "en")).toMatch(/No published deadline — apply fast/);
  });
  it("Capital One possible-closing note shows in English", () => {
    expect(programDeadlineNote(P("capital-one-strategy"), "en")).toContain("possible closing on Nov. 15, 2026");
    expect(programNotes(P("capital-one-strategy"), "en")).toContain("Graduation in Dec. 2027 or later");
  });
  it("FR keeps the original text", () => {
    expect(programDeadlineNote(P("capital-one-strategy"), "fr")).toBe(P("capital-one-strategy").deadline_note);
  });
  it("every program has an English translation", () => {
    for (const p of PROGRAMS) expect(programNotes(p, "en")).not.toBe(p.notes);
  });
  it("city labels", () => {
    expect(cityLabel("Londres", "en")).toBe("London");
    expect(cityLabel("États-Unis", "en")).toBe("United States");
    expect(cityLabel("Virtuel", "en")).toBe("Virtual");
    expect(cityLabel("Londres", "fr")).toBe("Londres");
  });
});
