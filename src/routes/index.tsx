import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { LogoStrip } from "@/components/LogoStrip";
import { ProgramCard, SectionHead } from "@/components/bits";
import { PROGRAMS } from "@/lib/programs";
import { closedLast, daysLeft, rank } from "@/lib/matching";
import { profileStore } from "@/lib/store";
import { useI18n } from "@/lib/i18n";
import { cityLabel } from "@/lib/localize";
import { ResetProfile } from "@/components/ResetProfile";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "StageScope — radar de stages finance, quant et tech" },
      { name: "description", content: "31 stages réels, filtrés selon ton profil, avec un score explicable de 0 à 100. Aucun compte requis." },
      { property: "og:title", content: "StageScope — 31 stages. Zéro bruit. Un seul match." },
      { property: "og:description", content: "Radar de stages pour étudiants de 1re et 2e année en finance, quant et tech." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Home,
});

function Home() {
  const { t, lang } = useI18n();
  const profile = profileStore.use();
  const ranked = useMemo(() => rank(PROGRAMS, profile), [profile]);
  const eligible = ranked.filter((r) => r.eligible).length;
  const upcoming = PROGRAMS.map((p) => daysLeft(p.deadline)).filter((d): d is number => d != null && d >= 0).sort((a, b) => a - b);
  const mtl = PROGRAMS.filter((p) => p.locations.includes("Montréal")).length;
  const top = closedLast(ranked).filter((r) => r.eligible).slice(0, 3);

  const kpis = [
    { v: String(PROGRAMS.length), l: t.kpi_programs },
    { v: String(eligible), l: t.kpi_eligible },
    { v: upcoming[0] != null ? t.days(upcoming[0]) : "—", l: t.kpi_next, warn: true },
    { v: String(mtl), l: t.kpi_mtl },
  ];
  const steps = [[t.how1_t, t.how1_d], [t.how2_t, t.how2_d], [t.how3_t, t.how3_d]];

  return (
    <>
      <section className="radar-grid relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          {[0, 1, 2].map((i) => <span key={i} className="sonar-ring" style={{ animationDelay: `${i * 2.3}s`, left: "78%", top: "45%" }} />)}
        </div>
        <div className="relative mx-auto max-w-7xl px-4 pb-14 pt-16 md:px-8 md:pt-24">
          <div className="font-mono text-xs uppercase tracking-[0.2em] text-primary">● {t.hero_kicker}</div>
          <h1 className="display mt-6 max-w-5xl text-6xl md:text-8xl lg:text-[8.5rem]">{t.tagline}</h1>
          <div className="mt-8 grid gap-8 md:grid-cols-[1fr_auto] md:items-end">
            <p className="max-w-xl text-base text-muted-foreground md:text-lg">{t.hero_sub}</p>
            <div className="flex flex-wrap gap-3 font-mono text-sm uppercase">
              <Link to="/trouve" className="bg-primary px-5 py-3 font-medium text-primary-foreground hover:opacity-90">{t.cta_find} →</Link>
              <Link to="/explorer" className="border border-border px-5 py-3 hover:border-primary">{t.cta_explore}</Link>
            </div>
          </div>
        </div>
        <div className="relative mx-auto grid max-w-7xl grid-cols-2 border-t border-dashed border-border md:grid-cols-4">
          {kpis.map((k, i) => (
            <div key={i} className="border-dashed border-border px-4 py-5 md:px-8 [&:not(:first-child)]:md:border-l">
              <div className={`font-mono text-3xl tabular-nums md:text-4xl ${k.warn ? "text-amber" : "text-primary"}`}>{k.v}</div>
              <div className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{k.l}</div>
            </div>
          ))}
        </div>
      </section>

      <LogoStrip />

      <section className="paper radar-grid">
        <div className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <div className="mb-6 flex justify-end"><ResetProfile /></div>
          <SectionHead n="01" title={t.top_title} sub={`${t.top_sub} · ${profile.school ?? ""} ${profile.grad} · ${cityLabel(profile.city, lang)}`} />
          <div className="grid gap-4 md:grid-cols-3">
            {top.map((r) => <ProgramCard key={r.program.id} r={r} showBreakdown />)}
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 md:px-8">
          <SectionHead n="02" title={t.how_title} />
          <ol className="grid gap-px bg-border md:grid-cols-3">
            {steps.map(([title, d], i) => (
              <li key={i} className="bg-background p-6">
                <div className="font-mono text-5xl text-primary">0{i + 1}</div>
                <h3 className="mt-6 font-display text-xl font-bold uppercase">{title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </>
  );
}
