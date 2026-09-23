import { translateApiError } from "./apiErrors";

export type Broker = { id: number; name: string };
export type Instrument = { id: number; name: string; active: boolean; currency: "COP" | "USD" };
export type Trade = {
  id: number;
  instrument_id: number;
  broker_id: number;
  type: "buy" | "sell";
  year: number;
  month: number | null;
  quantity: string;
  commission: string;
  price: string | null;
  instrument_name: string | null;
  broker_name: string | null;
  instrument_currency: "COP" | "USD" | null;
};
export type PendingPrices = {
  year: number;
  month: number;
  total_active: number;
  pending: number;
  missing: { instrument_id: number; instrument_name: string }[];
};
export type Price = {
  id: number;
  instrument_id: number;
  year: number;
  month: number;
  price: string;
  instrument_name: string | null;
  instrument_currency: "COP" | "USD" | null;
};
export type Position = {
  instrument_id: number;
  instrument_name: string;
  broker_id: number;
  broker_name: string;
  balance: string;
  last_price: string | null;
  price_year: number | null;
  price_month: number | null;
  value: string | null;
  weight_pct: string | null;
  missing_price: boolean;
  instrument_currency: "COP" | "USD";
};
export type Summary = { total: string; positions: Position[] };
export type TradePayload = {
  instrument_id: number;
  broker_id: number;
  type: "buy" | "sell";
  year: number;
  month: number | null;
  quantity: number;
  commission: number;
  price: number | null;
};
export type Target = {
  id: number;
  instrument_id: number;
  year: number;
  month: number;
  price: string;
  instrument_name: string | null;
  instrument_currency: "COP" | "USD" | null;
};
export type TargetProgress = {
  instrument_id: number;
  instrument_name: string;
  last_price: string | null;
  price_year: number | null;
  price_month: number | null;
  target: string | null;
  target_year: number | null;
  target_month: number | null;
  progress_pct: string | null;
  instrument_currency: "COP" | "USD";
};
export type Variation = {
  instrument_id: number;
  instrument_name: string;
  instrument_currency: "COP" | "USD";
  points: {
    year: number;
    month: number;
    price: string;
    variation_pct: string | null;
  }[];
};
export type FxRate = {
  id: number;
  year: number;
  month: number;
  cop_per_usd: string;
};

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = translateApiError(body.detail);
      else if (Array.isArray(body.detail)) msg = body.detail.map((d: { msg?: string }) => d.msg).join("; ");
    } catch {
      /* keep statusText */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ status: string }>("/health"),
  brokers: () => req<Broker[]>("/brokers"),
  createBroker: (name: string) =>
    req<Broker>("/brokers", { method: "POST", body: JSON.stringify({ name }) }),
  instruments: () => req<Instrument[]>("/instruments"),
  createInstrument: (name: string, currency: "COP" | "USD" = "COP") =>
    req<Instrument>("/instruments", { method: "POST", body: JSON.stringify({ name, active: true, currency }) }),
  patchInstrument: (id: number, body: { active?: boolean; name?: string; currency?: "COP" | "USD" }) =>
    req<Instrument>(`/instruments/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  trades: () => req<Trade[]>("/trades"),
  createTrade: (body: TradePayload) =>
    req<Trade>("/trades", { method: "POST", body: JSON.stringify(body) }),
  updateTrade: (id: number, body: TradePayload) =>
    req<Trade>(`/trades/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteTrade: (id: number) => req<void>(`/trades/${id}`, { method: "DELETE" }),
  prices: (year?: number) => req<Price[]>(year ? `/prices?year=${year}` : "/prices"),
  upsertPrice: (body: { instrument_id: number; year: number; month: number; price: number }) =>
    req<Price>("/prices", { method: "PUT", body: JSON.stringify(body) }),
  pendingPrices: (year: number, month: number) =>
    req<PendingPrices>(`/prices/pending?year=${year}&month=${month}`),
  summary: () => req<Summary>("/summary"),
  variation: (instrumentId: number) =>
    req<Variation>(`/price-variation?instrument_id=${instrumentId}`),
  targets: (instrumentId: number) => req<Target[]>(`/targets?instrument_id=${instrumentId}`),
  upsertTarget: (body: { instrument_id: number; year: number; month: number; price: number }) =>
    req<Target>("/targets", { method: "PUT", body: JSON.stringify(body) }),
  targetProgress: (instrumentId: number) =>
    req<TargetProgress>(`/target-progress?instrument_id=${instrumentId}`),
  fxRates: (year?: number) => req<FxRate[]>(year ? `/fx-rates?year=${year}` : "/fx-rates"),
  upsertFxRate: (body: { year: number; month: number; cop_per_usd: number }) =>
    req<FxRate>("/fx-rates", { method: "PUT", body: JSON.stringify(body) }),
};
