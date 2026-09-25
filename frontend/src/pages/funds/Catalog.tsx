import { FormEvent, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api, type Fiduciary, type Fund } from "../../api";

export default function FundsCatalog() {
  const { t } = useTranslation();
  const [funds, setFunds] = useState<Fund[]>([]);
  const [fiduciaries, setFiduciaries] = useState<Fiduciary[]>([]);
  const [fundName, setFundName] = useState("");
  const [fundCurrency, setFundCurrency] = useState<"COP" | "USD">("COP");
  const [fiduciaryName, setFiduciaryName] = useState("");
  const [editing, setEditing] = useState<{ kind: "fund" | "fiduciary"; id: number } | null>(null);
  const [draftName, setDraftName] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const [f, c] = await Promise.all([api.funds(), api.fiduciaries()]);
    setFunds(f);
    setFiduciaries(c);
  }

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, []);

  async function addFund(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.createFund(fundName.trim(), fundCurrency);
      setFundName("");
      setFundCurrency("COP");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  async function addFiduciary(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.createFiduciary(fiduciaryName.trim());
      setFiduciaryName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  async function toggleActive(row: Fund) {
    setError(null);
    try {
      await api.patchFund(row.id, { active: !row.active });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  function startEdit(kind: "fund" | "fiduciary", row: { id: number; name: string }) {
    setError(null);
    setEditing({ kind, id: row.id });
    setDraftName(row.name);
  }

  function cancelEdit() {
    setEditing(null);
    setDraftName("");
  }

  async function saveName(kind: "fund" | "fiduciary", row: { id: number; name: string }, e: FormEvent) {
    e.preventDefault();
    const name = draftName.trim();
    if (!name) return;
    if (name === row.name) {
      cancelEdit();
      return;
    }
    setError(null);
    try {
      if (kind === "fund") await api.patchFund(row.id, { name });
      else await api.patchFiduciary(row.id, name);
      cancelEdit();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  return (
    <div className="grid gap-8 md:grid-cols-2">
      {error && (
        <p className="md:col-span-2 rounded border border-down/40 bg-down/10 px-3 py-2 text-sm text-down">
          {error}
        </p>
      )}
      <section className="rounded-lg bg-surface p-4 shadow-sm">
        <h2 className="font-display text-xl">{t("funds.catalog.funds")}</h2>
        <form onSubmit={addFund} className="mt-3 flex flex-wrap gap-2">
          <input
            className="min-w-[10rem] flex-1 rounded border border-line px-3 py-2"
            value={fundName}
            onChange={(e) => setFundName(e.target.value)}
            placeholder={t("common.name")}
            required
          />
          <select
            className="rounded border border-line bg-surface-2 px-2 py-2 text-sm"
            value={fundCurrency}
            onChange={(e) => setFundCurrency(e.target.value as "COP" | "USD")}
            aria-label={t("funds.catalog.currency")}
          >
            <option value="COP">{t("currency.cop")}</option>
            <option value="USD">{t("currency.usd")}</option>
          </select>
          <button className="rounded bg-up px-3 py-2 text-sm text-white" type="submit">
            {t("common.add")}
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {funds.map((row) => (
            <li key={row.id} className="flex items-center justify-between gap-2 py-2">
              {editing?.kind === "fund" && editing.id === row.id ? (
                <form onSubmit={(e) => void saveName("fund", row, e)} className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
                  <input
                    className="min-w-[8rem] flex-1 rounded border border-line px-2 py-1"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    aria-label={t("common.name")}
                    autoFocus
                    required
                  />
                  <button className="text-sm text-accent underline" type="submit">
                    {t("common.save")}
                  </button>
                  <button className="text-sm text-muted underline" type="button" onClick={cancelEdit}>
                    {t("common.cancel")}
                  </button>
                </form>
              ) : (
                <>
                  <span className="min-w-0">
                    {row.name}{" "}
                    <span className="text-xs text-muted">
                      {row.currency} · {row.active ? t("common.active") : t("common.inactive")}
                    </span>
                  </span>
                  <span className="flex shrink-0 gap-3">
                    <button type="button" className="text-sm text-accent underline" onClick={() => startEdit("fund", row)}>
                      {t("common.edit")}
                    </button>
                    <button
                      type="button"
                      className="text-sm text-accent underline"
                      onClick={() => void toggleActive(row)}
                    >
                      {row.active ? t("common.inactivate") : t("common.activate")}
                    </button>
                  </span>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-lg bg-surface p-4 shadow-sm">
        <h2 className="font-display text-xl">{t("funds.catalog.fiduciaries")}</h2>
        <form onSubmit={addFiduciary} className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-line px-3 py-2"
            value={fiduciaryName}
            onChange={(e) => setFiduciaryName(e.target.value)}
            placeholder={t("common.name")}
            required
          />
          <button className="rounded bg-up px-3 py-2 text-sm text-white" type="submit">
            {t("common.add")}
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {fiduciaries.map((row) => (
            <li key={row.id} className="flex items-center justify-between gap-2 py-2">
              {editing?.kind === "fiduciary" && editing.id === row.id ? (
                <form onSubmit={(e) => void saveName("fiduciary", row, e)} className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
                  <input
                    className="min-w-[8rem] flex-1 rounded border border-line px-2 py-1"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    aria-label={t("common.name")}
                    autoFocus
                    required
                  />
                  <button className="text-sm text-accent underline" type="submit">
                    {t("common.save")}
                  </button>
                  <button className="text-sm text-muted underline" type="button" onClick={cancelEdit}>
                    {t("common.cancel")}
                  </button>
                </form>
              ) : (
                <>
                  <span className="min-w-0">{row.name}</span>
                  <button
                    type="button"
                    className="shrink-0 text-sm text-accent underline"
                    onClick={() => startEdit("fiduciary", row)}
                  >
                    {t("common.edit")}
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
