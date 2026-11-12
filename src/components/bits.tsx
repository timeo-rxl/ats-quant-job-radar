import { Link } from "@tanstack/react-router";
import { ArrowUpRight } from "lucide-react";
import type { Program } from "@/lib/types";
import { daysLeft, type Ranked, type ScoreBreakdown } from "@/lib/matching";
import { useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { Logo } from "./Logo";
import { cityLabel, programDeadlineNote } from "@/lib/localize";

export function Tag({ children, tone = "muted", className }: { children: React.ReactNode; tone?: "muted" | "ok" | "warn"; className?: string }) {
  return (
    <span className={cn("inline-flex items-center whitespace-nowrap font-mono text-[10px] uppercase tracking-wider",
      tone === "ok" && "text-primary", tone === "warn" && "text-amber", tone === "muted" && "text-muted-foreground", className)}>
      [{children}]
    </span>
  );
}

export function VerifyBadge({ p }: { p: Program }) {
  const { t } = useI18n();
  return p.verified ? <Tag tone="ok">{t.verified} {p.verified_date}</Tag> : <Tag tone="warn">{t.to_verify}</Tag>;
}

export function DeadlineLine({ p, full }: { p: Program; full?: boolean }) {
  const { t, lang } = useI18n();
  const dn = programDeadlineNote(p, lang);
  const d = daysLeft(p.deadline);
  if (p.deadline && d != null) {
    return (
      <div className="font-mono text-xs">
        <span className="text-foreground">{p.deadline}</span>{" "}
        {d < 0 ? <span className="text-muted-foreground">· {t.closed}</span>
          : <span className={d <= 30 ? "text-amber" : "text-primary"}>· {d === 0 ? t.today : t.days(d)}</span>}
        {full && dn && <p className="mt-1 text-muted-foreground">{dn}</p>}
      </div>
    );
  }
  const note = dn || t.no_deadline;
  return <p className={cn("font-mono text-xs text-muted-foreground", !full && "line-clamp-2")}>{note}</p>;
}

export function ScoreBar({ b }: { b: ScoreBreakdown }) {
  const { t } = useI18n();
  const parts = [
    { k: t.bd_elig, v: b.eligibility, c: "bg-primary" },
    { k: t.bd_int, v: b.interests, c: "bg-primary/60" },
    { k: t.bd_city, v: b.city, c: "bg-amber" },
    { k: t.bd_paid, v: b.paid, c: "bg-amber/50" },
  ];
  return (
    <div>
      <div className="flex h-2 w-full overflow-hidden bg-muted">
        {parts.map((p) => <div key={p.k} className={p.c} style={{ width: `${p.v}%` }} />)}
      </div>
      <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[10px] text-muted-foreground">
        {parts.map((p) => <span key={p.k}><span className={cn("mr-1 inline-block size-1.5", p.c)} />{p.k} {p.v}</span>)}
      </div>
    </div>
  );
}

export function ScoreNum({ r, className }: { r: Ranked; className?: string }) {
  return (
    <div className={cn("font-mono tabular-nums leading-none", r.eligible ? "text-primary" : "text-muted-foreground", className)}>
      {String(r.score).padStart(3, "0")}
    </div>
  );
}

export function SectionHead({ n, title, sub }: { n: string; title: string; sub?: string }) {
  return (
    <div className="mb-8 flex items-end justify-between gap-6 border-b border-dashed border-border pb-4">
      <div>
        <div className="font-mono text-xs text-muted-foreground">{n} /</div>
        <h2 className="display mt-2 text-4xl md:text-5xl">{title}</h2>
      </div>
      {sub && <div className="font-mono text-xs text-muted-foreground">{sub}</div>}
    </div>
  );
}

export function ProgramCard({ r, showBreakdown }: { r: Ranked; showBreakdown?: boolean }) {
  const { t, session, lang } = useI18n();
  const p = r.program;
  const closed = (daysLeft(p.deadline) ?? 0) < 0;
  return (
    <article className={cn("flex flex-col border border-border bg-card p-5 transition-colors hover:border-primary/60", closed && "opacity-60")}>
      <div className="flex items-start gap-4">
        <div className="flex size-12 shrink-0 items-center justify-center rounded-md bg-paper p-1.5">
          <Logo firm={p.firm} className="size-full text-xs" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{p.firm}</div>
          <Link to="/programme/$id" params={{ id: p.id }} className="mt-0.5 block font-display text-lg font-semibold leading-tight hover:text-primary">
            {p.program}
          </Link>
        </div>
        <ScoreNum r={r} className="text-2xl" />
      </div>
      <div className="mt-4 space-y-1 font-mono text-xs text-muted-foreground">
        <div>{p.locations.length ? p.locations.map((c) => cityLabel(c, lang)).join(" · ") : "—"}</div>
        <div>{p.sessions.map(session).join(" · ")}</div>
      </div>
      <div className="mt-3 border-t border-dashed border-border pt-3">
        <div className="mb-1.5"><VerifyBadge p={p} /></div>
        <DeadlineLine p={p} />
      </div>
      {showBreakdown && r.eligible && <div className="mt-3"><ScoreBar b={r.breakdown} /></div>}
      {!r.eligible && (
        <p className="mt-3 font-mono text-[11px] text-amber">
          {t.ineligible} — {r.reasons.map((x) => x[lang]).join(" ; ")}
        </p>
      )}
      <div className="mt-auto flex gap-2 pt-4">
        <a href={p.apply_url} target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-1 bg-primary px-3 py-1.5 font-mono text-xs font-medium uppercase text-primary-foreground hover:opacity-90">
          {t.apply} <ArrowUpRight className="size-3.5" />
        </a>
        <Link to="/programme/$id" params={{ id: p.id }}
          className="inline-flex items-center border border-border px-3 py-1.5 font-mono text-xs uppercase hover:border-primary">
          {t.details}
        </Link>
      </div>
    </article>
  );
}
