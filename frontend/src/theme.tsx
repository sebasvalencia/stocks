import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

export const THEME_KEY = "stocks.theme";
export const THEMES = ["dark", "light"] as const;
export type ThemeMode = (typeof THEMES)[number];

type Ctx = {
  theme: ThemeMode;
  setTheme: (mode: ThemeMode) => void;
};

const ThemeContext = createContext<Ctx | null>(null);

export function readTheme(): ThemeMode {
  const stored = localStorage.getItem(THEME_KEY) ?? localStorage.getItem("acciones.theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export function applyTheme(mode: ThemeMode): void {
  document.documentElement.dataset.theme = mode;
  document.documentElement.style.colorScheme = mode;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", mode === "dark" ? "#0B1120" : "#F8FAFC");
}

applyTheme(readTheme());

export function chartTheme(mode: ThemeMode) {
  if (mode === "light") {
    return {
      colors: ["#2563EB", "#059669", "#64748B", "#D97706", "#DC2626", "#38BDF8", "#34D399"],
      grid: "#E2E8F0",
      tick: "#64748B",
      tooltip: {
        contentStyle: { background: "#FFFFFF", border: "1px solid #E2E8F0", color: "#0F172A", borderRadius: 8 },
        itemStyle: { color: "#0F172A" },
        labelStyle: { color: "#0F172A" },
      },
      label: "#0F172A",
      series: "#2563EB",
    };
  }
  return {
    colors: ["#3B82F6", "#10B981", "#94A3B8", "#F59E0B", "#EF4444", "#60A5FA", "#34D399"],
    grid: "#334155",
    tick: "#94A3B8",
    tooltip: {
      contentStyle: { background: "#E2E8F0", border: "1px solid #94A3B8", color: "#0F172A", borderRadius: 8 },
      itemStyle: { color: "#0F172A" },
      labelStyle: { color: "#0F172A" },
    },
    label: "#F8FAFC",
    series: "#3B82F6",
  };
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>(() => readTheme());

  function setTheme(mode: ThemeMode) {
    setThemeState(mode);
    localStorage.setItem(THEME_KEY, mode);
    applyTheme(mode);
  }

  const value = useMemo(() => ({ theme, setTheme }), [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): Ctx {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme requires ThemeProvider");
  return ctx;
}
