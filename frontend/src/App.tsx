import { useTranslation } from "react-i18next";
import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { useCurrency } from "./currency";
import { LANGS, setLanguage, type Lang } from "./i18n";
import Catalog from "./pages/Catalog";
import FxRates from "./pages/FxRates";
import Prices from "./pages/Prices";
import Summary from "./pages/Summary";
import Trades from "./pages/Trades";

const link = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${
    isActive ? "bg-white text-ink" : "text-paper/90 hover:bg-white/15"
  }`;

const pill = (active: boolean) =>
  `rounded px-2 py-1 ${active ? "bg-white text-ink" : "text-paper/90 hover:bg-white/15"}`;

export default function App() {
  const { t, i18n } = useTranslation();
  const { currency, setCurrency } = useCurrency();

  return (
    <div className="min-h-screen">
      <header className="bg-rust text-paper shadow-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <h1 className="font-display text-2xl tracking-wide">{t("app.title")}</h1>
          <div className="flex flex-wrap items-center gap-3">
            <nav className="flex flex-wrap gap-1">
              <NavLink to="/" className={link} end>
                {t("nav.summary")}
              </NavLink>
              <NavLink to="/prices" className={link}>
                {t("nav.prices")}
              </NavLink>
              <NavLink to="/trades" className={link}>
                {t("nav.trades")}
              </NavLink>
              <NavLink to="/catalog" className={link}>
                {t("nav.catalog")}
              </NavLink>
              <NavLink to="/fx" className={link}>
                {t("nav.fx")}
              </NavLink>
            </nav>
            <div className="flex gap-1 text-xs" role="group" aria-label="Currency">
              {(["COP", "USD"] as const).map((c) => (
                <button key={c} type="button" className={pill(currency === c)} onClick={() => setCurrency(c)}>
                  {t(`currency.${c.toLowerCase()}`)}
                </button>
              ))}
            </div>
            <div className="flex gap-1 text-xs" role="group" aria-label="Language">
              {LANGS.map((lng) => (
                <button
                  key={lng}
                  type="button"
                  className={pill(i18n.language === lng)}
                  onClick={() => setLanguage(lng as Lang)}
                >
                  {t(`lang.${lng}`)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<Summary />} />
          <Route path="/prices" element={<Prices />} />
          <Route path="/trades" element={<Trades />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/fx" element={<FxRates />} />
          <Route path="/precios" element={<Navigate to="/prices" replace />} />
          <Route path="/movimientos" element={<Navigate to="/trades" replace />} />
          <Route path="/catalogo" element={<Navigate to="/catalog" replace />} />
        </Routes>
      </main>
    </div>
  );
}
