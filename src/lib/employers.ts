export interface Employer { name: string; domain: string; aliases?: string[] }
export const EMPLOYERS: Employer[] = [
  { name: "Anthropic", domain: "anthropic.com" },
  { name: "BMO", domain: "bmo.com" },
  { name: "BNP Paribas", domain: "bnpparibas.com" },
  { name: "Banque Nationale", domain: "bnc.ca" },
  { name: "Banque du Canada", domain: "banqueducanada.ca" },
  { name: "CPP Investments", domain: "cppinvestments.com" },
  { name: "Capital One", domain: "capitalone.com" },
  { name: "Citadel", domain: "citadel.com" },
  { name: "Desjardins", domain: "desjardins.com" },
  { name: "Electronic Arts", domain: "ea.com" },
  { name: "Experience Ventures", domain: "experienceventures.ca" },
  { name: "Front Row Ventures", domain: "frontrow.ventures" },
  { name: "Goldman Sachs", domain: "goldmansachs.com" },
  { name: "Google", domain: "google.com" },
  { name: "JPMorganChase", domain: "jpmorganchase.com" },
  { name: "Jane Street", domain: "janestreet.com" },
  { name: "Kleiner Perkins", domain: "kpcb.com" },
  { name: "Microsoft", domain: "microsoft.com" },
  { name: "Morgan Stanley", domain: "morganstanley.com" },
  { name: "NEXT Canada", domain: "nextcanada.com" },
  { name: "Optiver", domain: "optiver.com" },
  { name: "PSP Investissements", domain: "pspinvestments.com" },
  { name: "RBC", domain: "rbc.com" },
  { name: "Scotiabank", domain: "scotiabank.com" },
  { name: "TD", domain: "td.com" },
  { name: "Wealthsimple", domain: "wealthsimple.com" },
];
export function employerOf(firm: string): Employer {
  return (
    EMPLOYERS.find((e) => firm === e.name || firm.startsWith(e.name + " ")) ??
    { name: firm, domain: "" }
  );
}
export const initials = (name: string) =>
  name.split(/\s+/).filter((w) => /[A-Za-zÀ-ÿ]/.test(w[0] ?? "")).map((w) => w[0]).join("").slice(0, 3).toUpperCase();
