export type Interest =
  | "quant" | "markets" | "investment_banking" | "asset_management" | "fintech"
  | "venture_capital" | "ai" | "startups" | "corporate_finance" | "tech";
export type Category = "banking" | "quant" | "tech" | "vc_startup" | "public";
export type Session = "summer_2027" | "winter_2027" | "fall_2027" | "school_year" | "summer_2028";

export interface Program {
  id: string; firm: string; program: string; type: string; category: Category;
  locations: string[]; sessions: Session[]; paid: boolean | null;
  min_year: number | null; max_year: number | null;
  grad_not_before: string | null; grad_window: [string, string] | null;
  requires_us_auth: boolean; interests: Interest[];
  deadline: string | null; deadline_note: string; apply_url: string;
  verified: boolean; verified_date: string; notes: string;
}

export interface Profile {
  year: number; grad: string; city: string; usAuth: boolean; interests: Interest[]; school?: string;
}

export const INTERESTS: Interest[] = ["quant","markets","investment_banking","asset_management","fintech","venture_capital","ai","startups","corporate_finance","tech"];
export const CATEGORIES: Category[] = ["banking","quant","tech","vc_startup","public"];
export const SESSIONS: Session[] = ["summer_2027","winter_2027","fall_2027","school_year","summer_2028"];
