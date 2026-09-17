import { FormEvent, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api, type Broker, type Instrument } from "../api";

export default function Catalog() {
  const { t } = useTranslation();
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [brokers, setBrokers] = useState<Broker[]>([]);
  const [instrumentName, setInstrumentName] = useState("");
  const [brokerName, setBrokerName] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function load() {
    const [i, c] = await Promise.all([api.instruments(), api.brokers()]);
    setInstruments(i);
    setBrokers(c);
  }

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, []);

  async function addInstrument(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.createInstrument(instrumentName.trim());
      setInstrumentName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  async function addBroker(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.createBroker(brokerName.trim());
      setBrokerName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }

  async function toggleActive(row: Instrument) {
    setError(null);
    try {
      await api.patchInstrument(row.id, { active: !row.active });
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
        <h2 className="font-display text-xl">{t("catalog.instruments")}</h2>
        <form onSubmit={addInstrument} className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-line px-3 py-2"
            value={instrumentName}
            onChange={(e) => setInstrumentName(e.target.value)}
            placeholder={t("common.name")}
            required
          />
          <button className="rounded bg-up px-3 py-2 text-sm text-white" type="submit">
            {t("common.add")}
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {instruments.map((row) => (
            <li key={row.id} className="flex items-center justify-between py-2">
              <span>
                {row.name}{" "}
                <span className="text-xs text-muted">
                  {row.active ? t("common.active") : t("common.inactive")}
                </span>
              </span>
              <button
                type="button"
                className="text-sm text-accent underline"
                onClick={() => toggleActive(row)}
              >
                {row.active ? t("common.inactivate") : t("common.activate")}
              </button>
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-lg bg-surface p-4 shadow-sm">
        <h2 className="font-display text-xl">{t("catalog.brokers")}</h2>
        <form onSubmit={addBroker} className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-line px-3 py-2"
            value={brokerName}
            onChange={(e) => setBrokerName(e.target.value)}
            placeholder={t("common.name")}
            required
          />
          <button className="rounded bg-up px-3 py-2 text-sm text-white" type="submit">
            {t("common.add")}
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {brokers.map((row) => (
            <li key={row.id} className="py-2">
              {row.name}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
