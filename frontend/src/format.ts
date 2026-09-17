import type { FxRate } from "./api";
import i18n from "./i18n";

export type DisplayCurrency = "COP" | "USD";

export function asMoneyCurrency(value: string | null | undefined): DisplayCurrency {
  return value === "USD" ? "USD" : "COP";
}

export function numberLocale(): string {
  const lng = i18n.language;
  if (lng.startsWith("en")) return "en-US";
  if (lng.startsWith("it")) return "it-IT";
  return "es-CO";
}

export function formatNumber(n: number, opts?: Intl.NumberFormatOptions): string {
  return n.toLocaleString(numberLocale(), opts);
}

export function formatMoney(n: number, currency: DisplayCurrency = "COP"): string {
  return n.toLocaleString(numberLocale(), {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "USD" ? 2 : 0,
    minimumFractionDigits: currency === "USD" ? 2 : 0,
  });
}

export function rateFor(rates: FxRate[], year: number, month: number): number | null {
  const row = rates.find((r) => r.year === year && r.month === month);
  if (!row) return null;
  const n = Number(row.cop_per_usd);
  return n > 0 ? n : null;
}

export function convertMoney(
  amount: number,
  from: DisplayCurrency,
  to: DisplayCurrency,
  year: number | null | undefined,
  month: number | null | undefined,
  rates: FxRate[],
): number | null {
  if (from === to) return amount;
  if (year == null || month == null) return null;
  const rate = rateFor(rates, year, month);
  if (rate == null) return null;
  if (from === "COP" && to === "USD") return amount / rate;
  return amount * rate;
}

export function convertCop(
  cop: number,
  currency: DisplayCurrency,
  year: number | null | undefined,
  month: number | null | undefined,
  rates: FxRate[],
): number | null {
  return convertMoney(cop, "COP", currency, year, month, rates);
}
