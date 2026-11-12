import en from "@/data/programs.en.json";
import type { Program } from "./types";
import type { Lang } from "./store";

const EN = en as Record<string, { notes: string; deadline_note: string }>;
const CITY_EN: Record<string, string> = { Londres: "London", "États-Unis": "United States", Virtuel: "Virtual" };

export const programNotes = (p: Program, lang: Lang) => (lang === "en" ? EN[p.id]?.notes ?? p.notes : p.notes);
export const programDeadlineNote = (p: Program, lang: Lang) =>
  lang === "en" ? EN[p.id]?.deadline_note ?? p.deadline_note : p.deadline_note;
export const cityLabel = (c: string, lang: Lang) => (lang === "en" ? CITY_EN[c] ?? c : c);
