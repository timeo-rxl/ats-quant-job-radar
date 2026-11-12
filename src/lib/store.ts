import { useSyncExternalStore } from "react";
import type { Profile } from "./types";
import { DEFAULT_PROFILE } from "./matching";

export type Lang = "fr" | "en";
export type Status = "todo" | "applied" | "interview" | "offer" | "rejected";
export const STATUSES: Status[] = ["todo", "applied", "interview", "offer", "rejected"];
export type Tracker = Record<string, { status: Status; updated: string }>;

function makeStore<T>(key: string, initial: T) {
  let value = initial;
  let loaded = false;
  const subs = new Set<() => void>();
  const load = () => {
    if (loaded || typeof window === "undefined") return;
    loaded = true;
    try { const s = localStorage.getItem(key); if (s) value = JSON.parse(s); } catch { /* ignore */ }
  };
  return {
    use(): T {
      return useSyncExternalStore(
        (cb) => { subs.add(cb); return () => subs.delete(cb); },
        () => { load(); return value; },
        () => initial,
      );
    },
    set(next: T) {
      load(); value = next;
      try { localStorage.setItem(key, JSON.stringify(next)); } catch { /* ignore */ }
      subs.forEach((f) => f());
    },
    get(): T { load(); return value; },
  };
}

export const langStore = makeStore<Lang>("stagescope.lang", "fr");
export const profileStore = makeStore<Profile>("stagescope.profile", DEFAULT_PROFILE);
export const trackerStore = makeStore<Tracker>("stagescope.tracker", {});

export function setStatus(id: string, status: Status | null) {
  const t = { ...trackerStore.get() };
  if (status) t[id] = { status, updated: new Date().toISOString().slice(0, 10) };
  else delete t[id];
  trackerStore.set(t);
}
