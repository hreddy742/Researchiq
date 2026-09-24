export interface AgentStep {
  agent: string;
  status: "pending" | "running" | "complete" | "error";
  output: string;
  duration_ms: number;
}

export interface PricePoint {
  date: string;
  close: number;
}

export interface StockData {
  ticker: string;
  company_name: string;
  current_price: number;
  previous_close: number;
  change_percent: number;
  volume: number;
  market_cap: number | null;
  pe_ratio: number | null;
  week_52_high: number;
  week_52_low: number;
  price_history: PricePoint[];
  currency: string;
}

export interface NewsHeadline {
  title: string;
  link: string;
  published: string;
  source: string;
}

export interface NewsData {
  headlines: NewsHeadline[];
  fetched_at: string;
}

export interface Sentiment {
  score: number;
  label: "positive" | "neutral" | "negative";
  summary: string;
}

export interface FilingData {
  cik: string;
  company_name: string;
  latest_10k_date: string | null;
  latest_10k_url: string | null;
  found: boolean;
}

export type ResearchPhase = "idle" | "loading" | "complete" | "error";

export interface ResearchState {
  phase: ResearchPhase;
  agentSteps: AgentStep[];
  stockData: StockData | null;
  newsData: NewsData | null;
  sentiment: Sentiment | null;
  report: string;
  totalMs: number;
  error: string | null;
}
