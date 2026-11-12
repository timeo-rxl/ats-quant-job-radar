import { useEffect, useRef, useState } from "react";
import { employerOf, initials } from "@/lib/employers";
import { cn } from "@/lib/utils";

export function Monogram({ name, className }: { name: string; className?: string | undefined }) {
  return (
    <div className={cn("flex items-center justify-center rounded-md bg-phosphor font-display font-bold text-ink", className)}>
      {initials(name)}
    </div>
  );
}

/** Ordered logo sources for a domain; empty list when no domain is known. */
export function logoSources(domain: string): string[] {
  if (!domain) return [];
  return [
    `https://www.google.com/s2/favicons?domain=${domain}&sz=128`,
    `https://icons.duckduckgo.com/ip3/${domain}.ico`,
  ];
}

/** Warm the primary logo and its fallback without delaying interaction. */
export function preloadLogos(domains: string[]) {
  return domains.map((domain) => {
    const sources = logoSources(domain);
    const image = new Image();
    let index = 0;
    image.onerror = () => {
      index += 1;
      const next = sources[index];
      if (next) image.src = next;
    };
    const primary = sources[0];
    if (primary) image.src = primary;
    return image;
  });
}

export function Logo({ firm, className }: { firm: string; className?: string }) {
  const e = employerOf(firm);
  const sources = logoSources(e.domain);
  const [idx, setIdx] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const ref = useRef<HTMLImageElement>(null);
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete) {
      if (img.naturalWidth === 0) setIdx((i) => i + 1);
      else setLoaded(true);
    }
  }, [idx]);
  if (idx >= sources.length) return <Monogram name={e.name} className={className} />;
  return (
    <span className={cn("relative inline-flex items-center justify-center", className)}>
      {!loaded && <Monogram name={e.name} className="absolute inset-0 size-full" />}
      <img ref={ref} src={sources[idx]} alt={e.name} loading="eager"
        onLoad={() => setLoaded(true)}
        onError={() => { setLoaded(false); setIdx((i) => i + 1); }}
        className={cn("size-full object-contain", !loaded && "invisible")} />
    </span>
  );
}
