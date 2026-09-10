import { useEffect, useMemo, useState } from "react";
import {
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
import { api, type Instrumento, type Resumen, type Variacion } from "../api";

const COLORS = ["#c45c26", "#3d5a45", "#1c1915", "#8b6914", "#6b3fa0", "#2b6cb0", "#9b2c2c"];

function cop(n: number): string {
  return n.toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
}

export default function ResumenPage() {
  const [resumen, setResumen] = useState<Resumen | null>(null);
  const [instrumentos, setInstrumentos] = useState<Instrumento[]>([]);
  const [sel, setSel] = useState<number | "">("");
  const [variacion, setVariacion] = useState<Variacion | null>(null);
  const [error, setError] = useState<string | null>(null);

  const activos = useMemo(() => instrumentos.filter((i) => i.activo), [instrumentos]);

  useEffect(() => {
    Promise.all([api.resumen(), api.instrumentos()])
      .then(([r, i]) => {
        setResumen(r);
        setInstrumentos(i);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!activos.length) {
      if (sel !== "") setSel("");
      return;
    }
    if (sel === "" || !activos.some((i) => i.id === sel)) {
      setSel(activos[0].id);
    }
  }, [activos, sel]);

  useEffect(() => {
    if (sel === "") {
      setVariacion(null);
      return;
    }
    api.variacion(Number(sel)).then(setVariacion).catch((e: Error) => setError(e.message));
  }, [sel]);

  const pieData = useMemo(
    () =>
      (resumen?.posiciones ?? [])
        .filter((p) => p.valor !== null && Number(p.valor) > 0)
        .map((p) => ({
          name: `${p.instrumento_nombre} · ${p.corredor_nombre}`,
          value: Number(p.valor),
        })),
    [resumen],
  );

  const lineData = useMemo(
    () =>
      (variacion?.puntos ?? [])
        .filter((p) => p.variacion_pct !== null)
        .map((p) => ({
          periodo: `${p.anio}-${String(p.mes).padStart(2, "0")}`,
          variacion: Number(p.variacion_pct),
        })),
    [variacion],
  );

  return (
    <div className="space-y-6">
      {error && (
        <p className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}
      <section className="rounded-lg bg-white p-5 shadow-sm">
        <p className="text-sm uppercase tracking-wide text-ink/50">Total actual (títulos activos)</p>
        <p className="font-display text-4xl">{cop(Number(resumen?.total ?? 0))}</p>
      </section>
      <section className="overflow-x-auto rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">Posiciones</h2>
        <table className="mt-3 w-full text-left text-sm">
          <thead>
            <tr className="border-b text-ink/60">
              <th className="py-2">Título</th>
              <th>Corredor</th>
              <th className="text-right">Saldo</th>
              <th className="text-right">Último precio</th>
              <th className="text-right">Valor</th>
              <th className="text-right">Peso %</th>
            </tr>
          </thead>
          <tbody>
            {(resumen?.posiciones ?? []).map((p) => (
              <tr key={`${p.instrumento_id}-${p.corredor_id}`} className="border-b border-ink/10">
                <td className="py-2">{p.instrumento_nombre}</td>
                <td>{p.corredor_nombre}</td>
                <td className="text-right">{Number(p.saldo).toLocaleString("es-CO")}</td>
                <td className="text-right">
                  {p.sin_precio ? "sin precio" : Number(p.precio_ultimo).toLocaleString("es-CO")}
                </td>
                <td className="text-right">{p.valor === null ? "—" : cop(Number(p.valor))}</td>
                <td className="text-right">
                  {p.peso_pct === null ? "—" : `${Number(p.peso_pct).toFixed(1)}%`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg bg-white p-4 shadow-sm">
          <h2 className="font-display text-xl">Peso % del portafolio</h2>
          {pieData.length === 0 ? (
            <p className="mt-6 text-sm text-ink/50">No hay valores con precio para graficar.</p>
          ) : (
            <div className="h-72">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => cop(v)} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
        <section className="rounded-lg bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <h2 className="font-display text-xl">Variación % mensual</h2>
            <select
              className="rounded border border-ink/20 px-2 py-1 text-sm"
              value={sel}
              onChange={(e) => setSel(Number(e.target.value))}
              disabled={activos.length === 0}
            >
              {activos.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.nombre}
                </option>
              ))}
            </select>
          </div>
          {lineData.length === 0 ? (
            <p className="mt-6 text-sm text-ink/50">
              Falta el mes calendario anterior; no se inventa el punto.
            </p>
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
    </div>
  );
}
