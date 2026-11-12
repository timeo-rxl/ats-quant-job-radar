import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { ProgramCard } from "@/components/bits";
import { PROGRAMS, CITIES } from "@/lib/programs";
import { closedLast, rank } from "@/lib/matching";
import { employerOf } from "@/lib/employers";
import { profileStore } from "@/lib/store";
import { useI18n, INTEREST_LABELS } from "@/lib/i18n";
import { CATEGORIES, SESSIONS, type Category, type Session } from "@/lib/types";
import { cn } from "@/lib/utils";
import { cityLabel } from "@/lib/localize";
import { ResetProfile } from "@/components/ResetProfile";

export const Route = createFileRoute("/explorer")({
  validateSearch: (s: Record<string, unknown>): { firm?: string } =>
    typeof s["firm"] === "string" && s["firm"] ? { firm: s["firm"] } : {},
  head: () => ({
    meta: [
      { title: "Explorer les 31 programmes — StageScope" },
      { name: "description", content: "Filtre les stages par catégorie, session, ville, rémunération et admissibilité." },
      { property: "og:title", content: "Explorer — StageScope" },
      { property: "og:description", content: "31 programmes de stages en banque, quant, tech, VC et secteur public." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Explore,
});

const chip = (on: boolean) => cn("border px-2.5 py-1 font-mono text-xs", on ? "border-primary bg-primary text-primary-foreground" : "border-border text-muted-foreground hover:text-foreground");

function Explore() {
  const { t, lang, category, session } = useI18n();
  const { firm } = Route.useSearch();
  const profile = profileStore.use();
  const [cat, setCat] = useState<Category | null>(null);
  const [ses, setSes] = useState<Session | null>(null);
  const [city, setCity] = useState("");
  const [paidOnly, setPaidOnly] = useState(false);
  const [eligOnly, setEligOnly] = useState(false);
  const [q, setQ] = useState("");

  const list = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return closedLast(rank(PROGRAMS, profile)).filter(({ program: p, eligible }) => {
      if (firm && employerOf(p.firm).name !== firm) return false;
      if (cat && p.category !== cat) return false;
      if (ses && !p.sessions.includes(ses)) return false;
      if (city && !p.locations.includes(city)) return false;
      if (paidOnly && p.paid !== true) return false;
      if (eligOnly && !eligible) return false;
      if (needle) {
        const hay = [p.firm, p.program, ...p.interests, ...p.interests.flatMap((i) => INTEREST_LABELS[i])].join(" ").toLowerCase();
        if (!hay.includes(needle)) return false;
      }
      return true;
    });
  }, [profile, firm, cat, ses, city, paidOnly, eligOnly, q]);

  const reset = () => { setCat(null); setSes(null); setCity(""); setPaidOnly(false); setEligOnly(false); setQ(""); };

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 md:px-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-dashed border-border pb-6">
        <div>
          <div className="font-mono text-xs text-muted-foreground">03 /</div>
          <h1 className="display mt-2 text-5xl md:text-7xl">{t.nav_explore}</h1>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <div className="font-mono text-sm text-primary">{t.results_count(list.length)}</div>
          <ResetProfile />
        </div>
      </div>

      <div className="mt-6 space-y-4">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t.f_search}
          className="w-full border border-input bg-card px-4 py-3 font-mono text-sm outline-none placeholder:text-muted-foreground focus:border-primary" />
        <Row label={t.f_category}>
          <button type="button" className={chip(!cat)} onClick={() => setCat(null)}>{t.all}</button>
          {CATEGORIES.map((c) => <button key={c} type="button" className={chip(cat === c)} onClick={() => setCat(c)}>{category(c)}</button>)}
        </Row>
        <Row label={t.f_session}>
          <button type="button" className={chip(!ses)} onClick={() => setSes(null)}>{t.all}</button>
          {SESSIONS.map((s) => <button key={s} type="button" className={chip(ses === s)} onClick={() => setSes(s)}>{session(s)}</button>)}
        </Row>
        <Row label={t.f_city}>
          <select value={city} onChange={(e) => setCity(e.target.value)} className="border border-border bg-card px-2.5 py-1 font-mono text-xs">
            <option value="">{t.all}</option>
            {CITIES.map((c) => <option key={c} value={c}>{cityLabel(c, lang)}</option>)}
          </select>
          <button type="button" className={chip(paidOnly)} onClick={() => setPaidOnly(!paidOnly)}>{t.f_paid}</button>
          <button type="button" className={chip(eligOnly)} onClick={() => setEligOnly(!eligOnly)}>{t.f_eligible}</button>
          {firm && (
            <Link to="/explorer" search={{}} className={chip(true)}>{t.firm_filter} : {firm} ×</Link>
          )}
          <button type="button" onClick={reset} className="font-mono text-xs text-muted-foreground underline hover:text-foreground">{t.reset}</button>
        </Row>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {list.map((r) => <ProgramCard key={r.program.id} r={r} />)}
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="w-24 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
