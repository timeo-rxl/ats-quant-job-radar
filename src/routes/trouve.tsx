import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { ProgramCard, SectionHead } from "@/components/bits";
import { PROGRAMS, CITIES } from "@/lib/programs";
import { closedLast, rank } from "@/lib/matching";
import { profileStore } from "@/lib/store";
import { useI18n } from "@/lib/i18n";
import { INTERESTS, type Profile } from "@/lib/types";
import { cn } from "@/lib/utils";
import { cityLabel } from "@/lib/localize";
import { GraduationDate } from "@/components/GraduationDate";
import { ResetProfile } from "@/components/ResetProfile";

export const Route = createFileRoute("/trouve")({
  head: () => ({
    meta: [
      { title: "Trouve ton stage — StageScope" },
      { name: "description", content: "Cinq questions pour classer 31 programmes selon ton profil, avec la raison exacte de chaque refus." },
      { property: "og:title", content: "Trouve ton stage — StageScope" },
      { property: "og:description", content: "Classement personnalisé et explicable de 31 stages finance, quant et tech." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Find,
});

const opt = (active: boolean) =>
  cn("border px-4 py-3 text-left font-mono text-sm transition-colors", active ? "border-primary bg-primary text-primary-foreground" : "border-border hover:border-primary");

function Find() {
  const { t, lang, interest } = useI18n();
  const saved = profileStore.use();
  const [draft, setDraft] = useState<Profile | null>(null);
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const p = draft ?? saved;
  const upd = (patch: Partial<Profile>) => setDraft({ ...p, ...patch });
  const ranked = useMemo(() => closedLast(rank(PROGRAMS, saved)), [saved]);

  const cities = Array.from(new Set(["Montréal", "Toronto", ...CITIES])).filter((c) => !["Virtuel", "Canada", "États-Unis"].includes(c));
  const questions = [t.q_year, t.q_grad, t.q_interests, t.q_city, t.q_us];
  const validGrad = /^\d{4}-(0[1-9]|1[0-2])$/.test(p.grad);
  const canNext = step === 1 ? validGrad : step === 2 ? p.interests.length > 0 : true;

  if (done) {
    const ok = ranked.filter((r) => r.eligible);
    const blocked = ranked.filter((r) => !r.eligible);
    return (
      <div className="mx-auto max-w-7xl px-4 py-14 md:px-8">
        <div className="mb-6 flex justify-end"><ResetProfile onReset={() => setDraft(null)} /></div>
        <SectionHead n="01" title={t.results} sub={`${t.year_n(saved.year)} · ${saved.grad} · ${cityLabel(saved.city, lang)} · US ${saved.usAuth ? t.yes : t.no}`} />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {ok.map((r) => <ProgramCard key={r.program.id} r={r} showBreakdown />)}
        </div>
        <div className="mt-20">
          <SectionHead n="02" title={t.blockers} sub={`${blocked.length} / ${PROGRAMS.length}`} />
          {blocked.length === 0 ? <p className="font-mono text-sm">{t.blockers_none}</p> : (
            <ul className="divide-y divide-dashed divide-border border-y border-dashed border-border">
              {blocked.map((r) => (
                <li key={r.program.id} className="grid gap-2 py-4 md:grid-cols-[1fr_1.4fr]">
                  <Link to="/programme/$id" params={{ id: r.program.id }} className="hover:text-primary">
                    <span className="font-mono text-xs text-muted-foreground">{r.program.firm}</span>
                    <div className="font-display font-semibold">{r.program.program}</div>
                  </Link>
                  <ul className="space-y-1 font-mono text-xs text-amber">
                    {r.reasons.map((x, i) => <li key={i}>→ {x[lang]}</li>)}
                  </ul>
                </li>
              ))}
            </ul>
          )}
        </div>
        <button type="button" onClick={() => { setDone(false); setStep(0); }} className="mt-10 border border-border px-4 py-2 font-mono text-xs uppercase hover:border-primary">
          ↺ {t.restart}
        </button>
      </div>
    );
  }

  return (
    <div className="radar-grid">
      <div className="mx-auto max-w-3xl px-4 py-16 md:px-8">
        <div className="flex items-center justify-between font-mono text-xs text-muted-foreground">
          <span>{t.step} 0{step + 1} {t.of} 05</span>
          <span className="flex gap-1">{questions.map((_, i) => <span key={i} className={cn("h-1 w-8", i <= step ? "bg-primary" : "bg-muted")} />)}</span>
        </div>
        <h1 className="display mt-8 text-4xl md:text-6xl">{questions[step]}</h1>
        <div className="mt-10">
          {step === 0 && (
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              {[1, 2, 3, 4].map((y) => <button key={y} type="button" className={opt(p.year === y)} onClick={() => upd({ year: y })}>{t.year_n(y)}</button>)}
            </div>
          )}
          {step === 1 && (
            <GraduationDate value={p.grad} onChange={(grad) => upd({ grad })} />
          )}
          {step === 2 && (
            <div className="grid gap-2 md:grid-cols-2">
              {INTERESTS.map((k) => {
                const on = p.interests.includes(k);
                return (
                  <button key={k} type="button" className={opt(on)}
                    onClick={() => upd({ interests: on ? p.interests.filter((x) => x !== k) : [...p.interests, k] })}>
                    {on ? "■" : "□"} {interest(k)}
                  </button>
                );
              })}
            </div>
          )}
          {step === 3 && (
            <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
              {cities.map((c) => <button key={c} type="button" className={opt(p.city === c)} onClick={() => upd({ city: c })}>{cityLabel(c, lang)}</button>)}
            </div>
          )}
          {step === 4 && (
            <div className="grid grid-cols-2 gap-3 md:w-80">
              <button type="button" className={opt(p.usAuth)} onClick={() => upd({ usAuth: true })}>{t.yes}</button>
              <button type="button" className={opt(!p.usAuth)} onClick={() => upd({ usAuth: false })}>{t.no}</button>
            </div>
          )}
        </div>
        <div className="mt-12 flex justify-between border-t border-dashed border-border pt-6 font-mono text-sm uppercase">
          <button type="button" disabled={step === 0} onClick={() => setStep(step - 1)} className="px-2 py-2 text-muted-foreground hover:text-foreground disabled:opacity-30">← {t.back}</button>
          {step < 4 ? (
            <button type="button" disabled={!canNext} onClick={() => setStep(step + 1)} className="bg-primary px-5 py-2.5 text-primary-foreground disabled:opacity-40">{t.next} →</button>
          ) : (
            <button type="button" onClick={() => { profileStore.set(p); setDraft(null); setDone(true); window.scrollTo(0, 0); }}
              className="bg-primary px-5 py-2.5 text-primary-foreground">{t.see_results} →</button>
          )}
        </div>
      </div>
    </div>
  );
}
