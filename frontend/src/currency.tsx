import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type FxRate } from "./api";
import type { DisplayCurrency } from "./format";

const CURRENCY_KEY = "stocks.currency";

type Ctx = {
  currency: DisplayCurrency;
  setCurrency: (c: DisplayCurrency) => void;
  rates: FxRate[];
  refreshRates: () => void;
};

const CurrencyContext = createContext<Ctx | null>(null);

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [currency, setCurrencyState] = useState<DisplayCurrency>(() => {
    const stored = localStorage.getItem(CURRENCY_KEY) ?? localStorage.getItem("acciones.currency");
    return stored === "USD" ? "USD" : "COP";
  });
  const [rates, setRates] = useState<FxRate[]>([]);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    api.fxRates().then(setRates).catch(() => setRates([]));
  }, [tick]);

  function setCurrency(c: DisplayCurrency) {
    setCurrencyState(c);
    localStorage.setItem(CURRENCY_KEY, c);
  }

  return (
    <CurrencyContext.Provider
      value={{ currency, setCurrency, rates, refreshRates: () => setTick((n) => n + 1) }}
    >
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency(): Ctx {
  const ctx = useContext(CurrencyContext);
  if (!ctx) throw new Error("useCurrency requires CurrencyProvider");
  return ctx;
}
