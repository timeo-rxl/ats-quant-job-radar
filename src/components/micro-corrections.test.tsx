import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { ScoreBar } from "./bits";
import { GraduationDate } from "./GraduationDate";
import { ResetProfile } from "./ResetProfile";
import { boundedCardPosition } from "./LogoStrip";
import { preloadLogos } from "./Logo";
import { EMPLOYERS } from "@/lib/employers";
import { DEFAULT_PROFILE } from "@/lib/matching";
import { langStore, profileStore, trackerStore } from "@/lib/store";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  langStore.set("fr");
  profileStore.set(DEFAULT_PROFILE);
  trackerStore.set({});
});

describe("micro-corrections", () => {
  it("does not label the Toronto profile city bonus Montréal in either language", () => {
    profileStore.set({ ...DEFAULT_PROFILE, city: "Toronto" });
    const b = { eligibility: 50, interests: 30, city: 10, paid: 10, total: 100 };
    const view = render(<ScoreBar b={b} />);
    expect(screen.getByText("Ville 10")).toBeInTheDocument();
    expect(view.container.textContent).not.toContain("Montréal");
    cleanup();
    langStore.set("en");
    const english = render(<ScoreBar b={b} />);
    expect(screen.getByText("City 10")).toBeInTheDocument();
    expect(english.container.textContent).not.toContain("Montréal");
  });

  it("warms all 26 primary employer logo URLs", () => {
    const images: { src: string; onerror: (() => void) | null }[] = [];
    vi.stubGlobal("Image", class {
      src = "";
      onerror = null;
      constructor() { images.push(this); }
    });
    preloadLogos(EMPLOYERS.map((e) => e.domain));
    expect(images).toHaveLength(26);
    expect(images.map((image) => image.src)).toEqual(EMPLOYERS.map((e) => `https://www.google.com/s2/favicons?domain=${e.domain}&sz=128`));
  });

  it("keeps rotated 120 by 80 cards inside every edge on desktop and mobile", () => {
    for (const width of [375, 1280]) {
      for (const rot of [-12, 0, 12]) {
        const radians = rot * Math.PI / 180;
        const hw = 60 * Math.abs(Math.cos(radians)) + 40 * Math.abs(Math.sin(radians));
        const hh = 60 * Math.abs(Math.sin(radians)) + 40 * Math.abs(Math.cos(radians));
        for (const [x, y] of [[0, 0], [width, 360]] as [number, number][]) {
          const point = boundedCardPosition(x, y, rot, width, 360);
          expect(point.x - hw).toBeGreaterThanOrEqual(0);
          expect(point.x + hw).toBeLessThanOrEqual(width);
          expect(point.y - hh).toBeGreaterThanOrEqual(0);
          expect(point.y + hh).toBeLessThanOrEqual(360);
        }
      }
    }
  });

  it("accepts a directly typed year-month value", () => {
    langStore.set("en");
    const onChange = vi.fn();
    render(<GraduationDate value="2028-05" onChange={onChange} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "2029-06" } });
    expect(onChange).toHaveBeenCalledWith("2029-06");
  });

  it("restores the default profile in one click without changing language or tracker", () => {
    profileStore.set({ ...DEFAULT_PROFILE, city: "Toronto", year: 2, grad: "2028-05" });
    langStore.set("en");
    const tracker = { example: { status: "applied" as const, updated: "2026-11-12" } };
    trackerStore.set(tracker);
    render(<ResetProfile />);
    fireEvent.click(screen.getByRole("button"));
    expect(profileStore.get()).toEqual(DEFAULT_PROFILE);
    expect(langStore.get()).toBe("en");
    expect(trackerStore.get()).toEqual(tracker);
  });
});