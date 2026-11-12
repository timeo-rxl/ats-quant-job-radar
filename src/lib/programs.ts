import raw from "@/data/programs.json";
import type { Program } from "./types";
export const PROGRAMS = raw as unknown as Program[];
export const CITIES = Array.from(new Set(PROGRAMS.flatMap((p) => p.locations))).sort((a, b) => a.localeCompare(b, "fr"));
