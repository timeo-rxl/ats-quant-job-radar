import { createFileRoute, Link } from "@tanstack/react-router";
import { PROGRAMS } from "@/lib/programs";
import { setStatus, STATUSES, trackerStore, type Status } from "@/lib/store";
import { useI18n } from "@/lib/i18n";

export const Route = createFileRoute("/suivi")({
  head: () => ({
    meta: [
      { title: "Suivi des candidatures — StageScope" },
      { name: "description", content: "Suis tes candidatures de stage localement et exporte-les en CSV. Aucun compte." },
      { property: "og:title", content: "Suivi des candidatures — StageScope" },
      { property: "og:description", content: "Tableau de suivi local : à postuler, postulé, entretien, offre, refusé." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Track,
});

function Track() {
  const { t, session } = useI18n();
  const tracker = trackerStore.use();
  const rows = PROGRAMS.flatMap((p) => { const e = tracker[p.id]; return e ? [{ p, ...e }] : []; });
  const label = (s: Status) => t[`st_${s}`];

  const exportCsv = () => {
    const esc = (v: string) => `"${v.replace(/"/g, '""')}"`;
    const lines = [["firm", "program", "status", "updated", "deadline", "apply_url"].join(",")];
    rows.forEach((r) => lines.push([r.p.firm, r.p.program, label(r.status), r.updated, r.p.deadline ?? "", r.p.apply_url].map(esc).join(",")));
    const url = URL.createObjectURL(new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a"); a.href = url; a.download = "stagescope-suivi.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:px-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-dashed border-border pb-6">
        <div>
          <div className="font-mono text-xs text-muted-foreground">04 /</div>
          <h1 className="display mt-2 text-5xl md:text-7xl">{t.track_title}</h1>
        </div>
        <button type="button" disabled={!rows.length} onClick={exportCsv} className="border border-border px-4 py-2 font-mono text-xs uppercase hover:border-primary disabled:opacity-40">↓ {t.export_csv}</button>
      </div>
      <div className="mt-6 grid grid-cols-5 gap-px bg-border font-mono">
        {STATUSES.map((s) => (
          <div key={s} className="bg-background p-3">
            <div className="text-2xl text-primary tabular-nums">{rows.filter((r) => r.status === s).length}</div>
            <div className="text-[10px] uppercase text-muted-foreground">{label(s)}</div>
          </div>
        ))}
      </div>
      {rows.length === 0 ? (
        <p className="mt-10 font-mono text-sm text-muted-foreground">{t.track_empty} <Link to="/explorer" className="text-primary underline">{t.nav_explore} →</Link></p>
      ) : (
        <div className="mt-8 overflow-x-auto">
          <table className="w-full font-mono text-sm">
            <thead className="text-left text-[11px] uppercase text-muted-foreground">
              <tr className="border-b border-border">
                <th className="py-2 pr-4">{t.firm_filter}</th><th className="py-2 pr-4">{t.f_session}</th><th className="py-2 pr-4">{t.deadline}</th>
                <th className="py-2 pr-4">{t.status}</th><th className="py-2 pr-4">{t.updated}</th><th />
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.p.id} className="border-b border-dashed border-border">
                  <td className="py-3 pr-4"><Link to="/programme/$id" params={{ id: r.p.id }} className="hover:text-primary"><div className="text-xs text-muted-foreground">{r.p.firm}</div>{r.p.program}</Link></td>
                  <td className="py-3 pr-4 text-xs">{r.p.sessions.map(session).join(", ")}</td>
                  <td className="py-3 pr-4 text-xs">{r.p.deadline ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <select value={r.status} onChange={(e) => setStatus(r.p.id, e.target.value as Status)} className="border border-border bg-card px-2 py-1 text-xs">
                      {STATUSES.map((s) => <option key={s} value={s}>{label(s)}</option>)}
                    </select>
                  </td>
                  <td className="py-3 pr-4 text-xs text-muted-foreground">{r.updated}</td>
                  <td className="py-3 text-right"><button type="button" onClick={() => setStatus(r.p.id, null)} className="text-xs text-muted-foreground hover:text-destructive">{t.remove}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
