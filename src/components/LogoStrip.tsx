import { useEffect, useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { EMPLOYERS } from "@/lib/employers";
import { useI18n } from "@/lib/i18n";
import { Logo, preloadLogos } from "./Logo";
import { Button } from "@/components/ui/button";

interface Card { key: number; x: number; y: number; rot: number; idx: number; fading: boolean }
const MAX = 6;

export function boundedCardPosition(x: number, y: number, rot: number, width: number, height: number) {
  const radians = rot * Math.PI / 180;
  const halfWidth = 60 * Math.abs(Math.cos(radians)) + 40 * Math.abs(Math.sin(radians)) + 8;
  const halfHeight = 60 * Math.abs(Math.sin(radians)) + 40 * Math.abs(Math.cos(radians)) + 8;
  const clamp = (v: number, margin: number, size: number) => Math.max(margin, Math.min(size - margin, v));
  return { x: clamp(x, halfWidth, width), y: clamp(y, halfHeight, height) };
}

export function LogoStrip() {
  const { t } = useI18n();
  const nav = useNavigate();
  const ref = useRef<HTMLDivElement>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const seq = useRef(0);
  const last = useRef(0);
  const timers = useRef<number[]>([]);

  const spawn = (x: number, y: number) => {
    const el = ref.current;
    if (!el) return;
    const rot = Math.random() * 24 - 12;
    const position = boundedCardPosition(x, y + (Math.random() * 20 - 10), rot, el.clientWidth, el.clientHeight);
    const key = seq.current++;
    const card: Card = { key, ...position, rot, idx: key % EMPLOYERS.length, fading: false };
    setCards((cs) => {
      const live = cs.filter((c) => !c.fading);
      const toFade = new Set(live.length >= MAX ? live.slice(0, live.length - MAX + 1).map((c) => c.key) : []);
      return [...cs.map((c) => (toFade.has(c.key) ? { ...c, fading: true } : c)), card];
    });
    const fade = (k: number, delay: number) =>
      timers.current.push(window.setTimeout(() => setCards((cs) => cs.map((c) => (c.key === k ? { ...c, fading: true } : c))), delay));
    fade(key, 1200);
    timers.current.push(window.setTimeout(() => setCards((cs) => cs.filter((c) => c.key !== key)), 1650));
  };

  useEffect(() => {
    const images = preloadLogos(EMPLOYERS.map((e) => e.domain));
    const el = ref.current;
    const observer = new ResizeObserver(() => {
      if (el) setCards((cs) => cs.map((c) => ({ ...c, ...boundedCardPosition(c.x, c.y, c.rot, el.clientWidth, el.clientHeight) })));
    });
    if (el) observer.observe(el);
    const touch = window.matchMedia("(hover: none)").matches;
    let iv: number | undefined;
    if (touch) {
      iv = window.setInterval(() => {
        const el = ref.current; if (!el) return;
        const r = el.getBoundingClientRect();
        spawn(60 + Math.random() * (r.width - 120), 60 + Math.random() * (r.height - 120));
      }, 700);
    }
    const ts = timers.current;
    return () => {
      if (iv) clearInterval(iv);
      ts.forEach(clearTimeout);
      observer.disconnect();
      images.forEach((image) => { image.onerror = null; });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={ref}
      className="dot-grid relative h-[360px] w-full overflow-hidden border-y border-border select-none"
      onMouseMove={(e) => {
        const now = performance.now();
        if (now - last.current < 90) return;
        last.current = now;
        const r = e.currentTarget.getBoundingClientRect();
        spawn(e.clientX - r.left, e.clientY - r.top);
      }}
    >
      <p className="pointer-events-none absolute inset-0 flex items-center justify-center px-4 text-center font-mono text-xs tracking-[0.2em] text-muted-foreground">
        {t.strip_label}<span className="cursor-blink ml-1 text-phosphor">_</span>
      </p>
      {cards.map((c) => {
        const e = EMPLOYERS[c.idx];
        if (!e) return null;
        return (
          <Button
            key={c.key}
            type="button"
            data-fading={c.fading}
            variant="ghost"
            className="logo-card flex h-[80px] w-[120px] flex-col items-center justify-center gap-1.5 p-2"
            style={{ left: c.x, top: c.y, ["--rot" as string]: `${c.rot}deg` }}
            onClick={() => nav({ to: "/explorer", search: { firm: e.name } })}
          >
            <Logo firm={e.name} className="h-9 w-20 text-sm" />
            <span className="max-w-full truncate font-mono text-[10px] leading-none">{e.name}</span>
          </Button>
        );
      })}
    </div>
  );
}
