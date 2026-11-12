import { describe, expect, it } from "vitest";
import { logoSources } from "./Logo";
import { employerOf } from "@/lib/employers";

describe("logoSources", () => {
  it("builds the Google favicons URL as primary source for BNP Paribas", () => {
    const sources = logoSources(employerOf("BNP Paribas").domain);
    expect(sources[0]).toBe("https://www.google.com/s2/favicons?domain=bnpparibas.com&sz=128");
  });

  it("uses DuckDuckGo icons as the second fallback", () => {
    const sources = logoSources(employerOf("BNP Paribas").domain);
    expect(sources[1]).toBe("https://icons.duckduckgo.com/ip3/bnpparibas.com.ico");
  });

  it("returns no sources when the domain is unknown (monogram fallback)", () => {
    expect(logoSources("")).toEqual([]);
  });
});
