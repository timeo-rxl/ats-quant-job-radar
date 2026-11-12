import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowUpRight } from "lucide-react";
import { DeadlineLine, ScoreBar, ScoreNum, VerifyBadge } from "@/components/bits";
import { Logo } from "@/components/Logo";
import { PROGRAMS } from "@/lib/programs";
import { rank } from "@/lib/matching";
import { profileStore, setStatus, trackerStore } from "@/lib/store";
import { useI18n } from "@/lib/i18n";
import { cityLabel, programNotes } from "@/lib/localize";
import { ResetProfile } from "@/components/ResetProfile";

export const Route = createFileRoute("/programme/$id")({
  loader: ({ params }) => {
    const p = PROGRAMS.find((x) => x.id === params.id);
    if (!p) throw notFound();
    return { id: p.id, firm: p.firm, program: p.program };
  },
  head: ({ loaderData }) => ({
    meta: loaderData
      ? [
          { title: `${loaderData.firm} — ${loaderData.program} · StageScope` },
          { name: "description", content: `Admissibilité, deadline vérifiée et lien officiel : ${loaderData.firm} ${loaderData.program}.` },
          { property: "og:title", content: `${loaderData.firm} — ${loaderData.program}` },
          { property: "og:description", content: "Fiche programme StageScope : qui peut postuler, deadline, lien officiel." },
          { property: "og:type", content: "article" },
          { name: "twitter:card", content: "summary_large_image" },
        ]
      : [{ title: "Programme indisponible · StageScope" }, { name: "robots", content: "noindex" }],
  }),
  notFoundComponent: () => (
    <div className="mx-auto max-w-3xl px-4 py-24 font-mono">Programme introuvable / Program not found. <Link to="/explorer" className="text-primary underline">Explorer</Link></div>
  ),
  component: Detail,
});

function Detail() {
  const { id } = Route.useLoaderData();
  const { t, lang, interest, session } = useI18n();
  const profile = profileStore.use();
  const tracker = trackerStore.use();
  const r = rank(PROGRAMS, profile).find((x) => x.program.id === id);
  if (!r) return null;
  const p = r.program;
  const tracked = tracker[id];

  const rows: [string, string][] = [
    [t.min_year, p.min_year != null ? t.year_n(p.min_year) : t.none],
    [t.max_year, p.max_year != null ? t.year_n(p.max_year) : t.none],
    [t.grad, p.grad_not_before ? `${t.from} ${p.grad_not_before}` : p.grad_window ? `${t.between} ${p.grad_window[0]} ${t.and} ${p.grad_window[1]}` : t.none],
    [t.us_auth, p.requires_us_auth ? t.required : t.not_required],
    [t.locations, p.locations.map((c) => cityLabel(c, lang)).join(" · ") || t.none],
    [t.sessions, p.sessions.map(session).join(" · ")],
  ];

  return (
    <div className="radar-grid">
      <div className="mx-auto max-w-5xl px-4 py-12 md:px-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link to="/explorer" search={{}} className="font-mono text-xs text-muted-foreground hover:text-foreground">← {t.nav_explore}</Link>
          <ResetProfile />
        </div>
        <div className="mt-6 flex flex-wrap items-start gap-6">
          <div className="flex size-20 items-center justify-center rounded-lg bg-paper p-2"><Logo firm={p.firm} className="size-full text-lg" /></div>
          <div className="min-w-0 flex-1">
            <div className="font-mono text-xs uppercase tracking-wider text-muted-foreground">{p.firm}</div>
            <h1 className="display mt-2 text-4xl md:text-6xl">{p.program}</h1>
            <div className="mt-3 flex flex-wrap gap-3 font-mono text-xs">
              <VerifyBadge p={p} />
              <span className="text-muted-foreground">[{p.paid === true ? t.paid : p.paid === false ? t.unpaid : t.paid_unknown}]</span>
            </div>
          </div>
          <div className="text-right">
            <ScoreNum r={r} className="text-6xl" />
            <div className="mt-1 font-mono text-[10px] uppercase text-muted-foreground">{t.score} · {t.eligibility_you}</div>
          </div>
        </div>

        <div className="mt-8 border border-border bg-card p-5">
          {r.eligible ? <ScoreBar b={r.breakdown} /> : (
            <ul className="space-y-1 font-mono text-sm text-amber">
              <li className="uppercase">{t.ineligible}</li>
              {r.reasons.map((x, i) => <li key={i}>→ {x[lang]}</li>)}
            </ul>
          )}
        </div>

        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <section>
            <h2 className="font-mono text-xs uppercase tracking-wider text-muted-foreground">01 / {t.who}</h2>
            <dl className="mt-3 divide-y divide-dashed divide-border border-y border-dashed border-border font-mono text-sm">
              {rows.map(([k, v]) => <div key={k} className="flex justify-between gap-4 py-2.5"><dt className="text-muted-foreground">{k}</dt><dd className="text-right">{v}</dd></div>)}
            </dl>
            <h2 className="mt-8 font-mono text-xs uppercase tracking-wider text-muted-foreground">02 / {t.interests}</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {p.interests.map((i) => (
                <span key={i} className={`border px-2 py-1 font-mono text-xs ${profile.interests.includes(i) ? "border-primary text-primary" : "border-border text-muted-foreground"}`}>{interest(i)}</span>
              ))}
            </div>
          </section>
          <section>
            <h2 className="font-mono text-xs uppercase tracking-wider text-muted-foreground">03 / {t.deadline}</h2>
            <div className="mt-3"><DeadlineLine p={p} full /></div>
            <h2 className="mt-8 font-mono text-xs uppercase tracking-wider text-muted-foreground">04 / {t.status}</h2>
            <p className="mt-3 font-mono text-sm">{p.verified ? `${t.verified} — ${t.verified_on} ${p.verified_date}` : t.to_verify}</p>
            <h2 className="mt-8 font-mono text-xs uppercase tracking-wider text-muted-foreground">05 / {t.notes}</h2>
            <p className="mt-3 text-sm leading-relaxed">{programNotes(p, lang)}</p>
          </section>
        </div>

        <div className="mt-10 flex flex-wrap gap-3 border-t border-dashed border-border pt-6 font-mono text-sm uppercase">
          <a href={p.apply_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 bg-primary px-5 py-3 text-primary-foreground hover:opacity-90">
            {t.official} <ArrowUpRight className="size-4" />
          </a>
          {tracked ? (
            <Link to="/suivi" className="border border-primary px-5 py-3 text-primary">✓ {t.in_tracker} · {t[`st_${tracked.status}`]}</Link>
          ) : (
            <button type="button" onClick={() => setStatus(p.id, "applied")} className="border border-border px-5 py-3 hover:border-primary">{t.mark_applied}</button>
          )}
        </div>
        <p className="mt-3 break-all font-mono text-[11px] text-muted-foreground">{p.apply_url}</p>
      </div>
    </div>
  );
}
