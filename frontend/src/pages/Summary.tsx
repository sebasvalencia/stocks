import { FormEvent, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import BannerPrecios from "../BannerPrecios";
import { api, type Instrument, type Summary, type Target, type TargetProgress, type Variation } from "../api";
import { useCurrency } from "../currency";
import { convertCop, formatMoney, formatNumber } from "../format";

const COLORS = ["#c45c26", "#3d5a45", "#1c1915", "#8b6914", "#6b3fa0", "#2b6cb0", "#9b2c2c"];

export default function SummaryPage() {
  const { t } = useTranslation();
  const { currency, rates } = useCurrency();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [sel, setSel] = useState<number | "">("");
  const [variation, setVariation] = useState<Variation | null>(null);
  const [progress, setProgress] = useState<TargetProgress | null>(null);
  const [targets, setTargets] = useState<Target[]>([]);
  const [objYear, setObjYear] = useState("2026");
  const [objMonth, setObjMonth] = useState("9");
  const [objPrice, setObjPrice] = useState("");
  const [error, setError] = useState<string | null>(null);

  const active = useMemo(() => instruments.filter((i) => i.active), [instruments]);

  useEffect(() => {
    Promise.all([api.summary(), api.instruments()])
      .then(([r, i]) => {
        setSummary(r);
        setInstruments(i);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!active.length) {
      if (sel !== "") setSel("");
      return;
    }
    if (sel === "" || !active.some((i) => i.id === sel)) {
      setSel(active[0].id);
    }
  }, [active, sel]);

  useEffect(() => {
    if (sel === "") {
      setVariation(null);
      setProgress(null);
      setTargets([]);
      return;
    }
    Promise.all([
      api.variation(Number(sel)),
      api.targetProgress(Number(sel)),
      api.targets(Number(sel)),
    ])
      .then(([v, a, o]) => {
        setVariation(v);
        setProgress(a);
        setTargets(o);
      })
      .catch((e: Error) => setError(e.message));
  }, [sel]);

  const displayPositions = useMemo(() => {
    return (summary?.positions ?? []).map((p) => {
      const last = p.last_price == null
        ? null
        : convertCop(Number(p.last_price), currency, p.price_year, p.price_month, rates);
      const value = p.value == null
        ? null
        : convertCop(Number(p.value), currency, p.price_year, p.price_month, rates);
      return { ...p, lastDisplay: last, valueDisplay: value };
    });
  }, [summary, currency, rates]);

  const usdReady = displayPositions.filter((p) => p.valueDisplay != null);
  const displayTotal = usdReady.reduce((acc, p) => acc + (p.valueDisplay ?? 0), 0);

  const pieData = useMemo(
    () =>
      usdReady
        .filter((p) => (p.valueDisplay ?? 0) > 0)
        .map((p) => ({
          name: `${p.instrument_name} · ${p.broker_name}`,
          value: p.valueDisplay ?? 0,
        })),
    [usdReady],
  );

  async function reloadTarget() {
    if (sel === "") return;
    const [a, o] = await Promise.all([api.targetProgress(Number(sel)), api.targets(Number(sel))]);
    setProgress(a);
    setTargets(o);
  }

  async function saveTarget(e: FormEvent) {
    e.preventDefault();
    if (sel === "") return;
    setError(null);
    try {
      await api.upsertTarget({
        instrument_id: Number(sel),
        year: Number(objYear),
        month: Number(objMonth),
        price: Number(objPrice),
      });
      setObjPrice("");
      await reloadTarget();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  const marketDisplay = progress?.last_price == null
    ? null
    : convertCop(Number(progress.last_price), currency, progress.price_year, progress.price_month, rates);
  const targetDisplay = progress?.target == null
    ? null
    : convertCop(Number(progress.target), currency, progress.target_year, progress.target_month, rates);

  const barTarget = useMemo(() => {
    if (marketDisplay == null || targetDisplay == null) return [];
    return [
      { name: t("summary.market"), valor: marketDisplay },
      { name: t("summary.target"), valor: targetDisplay },
    ];
  }, [marketDisplay, targetDisplay, t]);

  const pctProgress = progress?.progress_pct == null ? null : Number(progress.progress_pct);
  const barPct = pctProgress == null ? 0 : Math.min(pctProgress, 100);

  const lineData = useMemo(
    () =>
      (variation?.points ?? [])
        .filter((p) => p.variation_pct !== null)
        .map((p) => ({
          periodo: `${p.year}-${String(p.month).padStart(2, "0")}`,
          variacion: Number(p.variation_pct),
        })),
    [variation],
  );

  function moneyOrMissing(n: number | null, fallback: string): string {
    if (n == null) return fallback;
    return formatMoney(n, currency);
  }

  return (
    <div className="space-y-6">
      <BannerPrecios linkToPrices />
      {error && (
        <p className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}
      <section className="rounded-lg bg-white p-5 shadow-sm">
        <p className="text-sm uppercase tracking-wide text-ink/50">{t("summary.total")}</p>
        <p className="font-display text-4xl">{formatMoney(displayTotal, currency)}</p>
      </section>
      <section className="overflow-x-auto rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">{t("summary.positions")}</h2>
        <table className="mt-3 w-full text-left text-sm">
          <thead>
            <tr className="border-b text-ink/60">
              <th className="py-2">{t("summary.instrument")}</th>
              <th>{t("summary.broker")}</th>
              <th className="text-right">{t("summary.balance")}</th>
              <th className="text-right">{t("summary.lastPrice")}</th>
              <th className="text-right">{t("summary.value")}</th>
              <th className="text-right">{t("summary.weight")}</th>
            </tr>
          </thead>
          <tbody>
            {displayPositions.map((p) => {
              const weight =
                p.valueDisplay == null || displayTotal === 0
                  ? null
                  : (p.valueDisplay / displayTotal) * 100;
              return (
                <tr key={`${p.instrument_id}-${p.broker_id}`} className="border-b border-ink/10">
                  <td className="py-2">{p.instrument_name}</td>
                  <td>{p.broker_name}</td>
                  <td className="text-right">{formatNumber(Number(p.balance))}</td>
                  <td className="text-right">
                    {p.missing_price
                      ? t("summary.noPrice")
                      : moneyOrMissing(p.lastDisplay, t("fx.missing"))}
                  </td>
                  <td className="text-right">
                    {p.missing_price
                      ? t("common.dash")
                      : moneyOrMissing(p.valueDisplay, t("fx.missing"))}
                  </td>
                  <td className="text-right">
                    {weight == null ? t("common.dash") : `${weight.toFixed(1)}%`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg bg-white p-4 shadow-sm">
          <h2 className="font-display text-xl">{t("summary.pieTitle")}</h2>
          {pieData.length === 0 ? (
            <p className="mt-6 text-sm text-ink/50">{t("summary.pieEmpty")}</p>
          ) : (
            <div className="h-72">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatMoney(v, currency)} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
        <section className="rounded-lg bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <h2 className="font-display text-xl">{t("summary.variationTitle")}</h2>
            <select
              className="rounded border border-ink/20 px-2 py-1 text-sm"
              value={sel}
              onChange={(e) => setSel(Number(e.target.value))}
              disabled={active.length === 0}
            >
              {active.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.name}
                </option>
              ))}
            </select>
          </div>
          {lineData.length === 0 ? (
            <p className="mt-6 text-sm text-ink/50">{t("summary.variationEmpty")}</p>
          ) : (
            <div className="h-72">
              <ResponsiveContainer>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="periodo" />
                  <YAxis unit="%" />
                  <Tooltip />
                  <Line type="monotone" dataKey="variacion" stroke="#c45c26" dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
      </div>
      <section className="rounded-lg bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display text-xl">{t("summary.targetTitle")}</h2>
          <select
            className="rounded border border-ink/20 px-2 py-1 text-sm"
            value={sel}
            onChange={(e) => setSel(Number(e.target.value))}
            disabled={active.length === 0}
          >
            {active.map((i) => (
              <option key={i.id} value={i.id}>
                {i.name}
              </option>
            ))}
          </select>
        </div>
        <form onSubmit={saveTarget} className="mt-4 grid gap-3 sm:grid-cols-4">
          <label className="text-sm">
            {t("common.year")}
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              value={objYear}
              onChange={(e) => setObjYear(e.target.value)}
              required
            />
          </label>
          <label className="text-sm">
            {t("common.month")}
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              min={1}
              max={12}
              value={objMonth}
              onChange={(e) => setObjMonth(e.target.value)}
              required
            />
          </label>
          <label className="text-sm">
            {t("summary.targetPrice", { currency: "COP" })}
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              min={0.0001}
              step="any"
              value={objPrice}
              onChange={(e) => setObjPrice(e.target.value)}
              required
            />
          </label>
          <div className="flex items-end">
            <button className="rounded bg-rust px-4 py-2 text-sm text-white" type="submit" disabled={sel === ""}>
              {t("summary.saveTarget")}
            </button>
          </div>
        </form>
        {pctProgress == null ? (
          <p className="mt-4 text-sm text-ink/50">{t("summary.targetEmpty")}</p>
        ) : (
          <div className="mt-4 grid gap-6 lg:grid-cols-2">
            <div>
              <p className="text-sm text-ink/50">{t("summary.targetVs")}</p>
              <p className="font-display text-3xl">{pctProgress.toFixed(1)}%</p>
              <p className="mt-1 text-sm text-ink/60">
                {moneyOrMissing(marketDisplay, t("fx.missing"))} / {moneyOrMissing(targetDisplay, t("fx.missing"))}
              </p>
              <div className="mt-3 h-3 overflow-hidden rounded bg-ink/10">
                <div className="h-full bg-rust" style={{ width: `${barPct}%` }} />
              </div>
            </div>
            {barTarget.length > 0 && (
              <div className="h-48">
                <ResponsiveContainer>
                  <BarChart data={barTarget}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(v: number) => formatMoney(v, currency)} />
                    <Bar dataKey="valor" fill="#c45c26" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
        {targets.length > 0 && (
          <table className="mt-6 w-full text-left text-sm">
            <thead>
              <tr className="border-b text-ink/60">
                <th className="py-2">{t("summary.period")}</th>
                <th className="text-right">{t("summary.target")}</th>
              </tr>
            </thead>
            <tbody>
              {targets.map((o) => {
                const shown = convertCop(Number(o.price), currency, o.year, o.month, rates);
                return (
                  <tr key={o.id} className="border-b border-ink/10">
                    <td className="py-2">
                      {o.year}-{String(o.month).padStart(2, "0")}
                    </td>
                    <td className="text-right">
                      {shown == null ? t("fx.missing") : formatMoney(shown, currency)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
