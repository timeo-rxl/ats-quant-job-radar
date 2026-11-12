import { useEffect } from "react";
import { Link } from "@tanstack/react-router";
import { useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function SiteNav() {
  const { t, lang, setLang } = useI18n();
  useEffect(() => { document.documentElement.lang = lang; }, [lang]);
  const links = [
    { to: "/", label: t.nav_home },
    { to: "/trouve", label: t.nav_find },
    { to: "/explorer", label: t.nav_explore },
    { to: "/suivi", label: t.nav_track },
  ] as const;
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-6 px-4 md:px-8">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold tracking-tight">
          <span className="relative flex size-3"><span className="absolute inset-0 animate-ping rounded-full bg-primary/50" /><span className="relative size-3 rounded-full bg-primary" /></span>
          STAGESCOPE
        </Link>
        <nav className="ml-auto flex items-center gap-1 overflow-x-auto font-mono text-xs uppercase">
          {links.map((l) => (
            <Link key={l.to} to={l.to} activeOptions={{ exact: l.to === "/" }}
              className="whitespace-nowrap px-2.5 py-1.5 text-muted-foreground hover:text-foreground"
              activeProps={{ className: "text-primary" }}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex border border-border font-mono text-xs" role="group" aria-label="Langue / Language">
          {(["fr", "en"] as const).map((l) => (
            <button key={l} type="button" onClick={() => setLang(l)} aria-pressed={lang === l}
              className={cn("px-2 py-1 uppercase", lang === l ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground")}>
              {l}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  const { t } = useI18n();
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-8 font-mono text-xs text-muted-foreground md:flex-row md:items-center md:justify-between md:px-8">
        <span>{t.footer}</span>
        <span>STAGESCOPE · {t.tagline}</span>
      </div>
    </footer>
  );
}
