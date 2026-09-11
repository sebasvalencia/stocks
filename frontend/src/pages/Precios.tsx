import { FormEvent, useEffect, useState } from "react";
import BannerPrecios, { mesCurso } from "../BannerPrecios";
import { api, type Instrumento, type Precio } from "../api";

const MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

export default function Precios() {
  const curso = mesCurso();
  const [anio, setAnio] = useState(curso.anio);
  const [instrumentos, setInstrumentos] = useState<Instrumento[]>([]);
  const [precios, setPrecios] = useState<Precio[]>([]);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [aviso, setAviso] = useState(0);

  async function cargar(y: number) {
    const [i, p] = await Promise.all([api.instrumentos(), api.precios(y)]);
    setInstrumentos(i);
    setPrecios(p);
  }

  useEffect(() => {
    cargar(anio).catch((e: Error) => setError(e.message));
  }, [anio]);

  function valor(instrumentoId: number, mes: number): string {
    const key = `${instrumentoId}-${mes}`;
    if (key in draft) return draft[key];
    const found = precios.find((p) => p.instrumento_id === instrumentoId && p.mes === mes);
    if (!found) return "";
    const n = Number(found.precio);
    return Number.isFinite(n) ? String(n) : found.precio;
  }

  async function guardar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setOk(null);
    try {
      for (const [key, raw] of Object.entries(draft)) {
        if (raw.trim() === "") continue;
        const [id, mes] = key.split("-").map(Number);
        await api.upsertPrecio({
          instrumento_id: id,
          anio,
          mes,
          precio: Number(raw),
        });
      }
      setDraft({});
      await cargar(anio);
      setAviso((n) => n + 1);
      setOk("Precios guardados");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <form onSubmit={guardar} className="space-y-4">
      <BannerPrecios recargar={aviso} />
      {error && (
        <p className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}
      {ok && <p className="rounded border border-moss/30 bg-moss/10 px-3 py-2 text-sm">{ok}</p>}
      <div className="flex items-end gap-3">
        <label className="text-sm">
          Año
          <input
            className="ml-2 rounded border border-ink/20 px-2 py-1"
            type="number"
            value={anio}
            onChange={(e) => setAnio(Number(e.target.value))}
          />
        </label>
        <button className="rounded bg-rust px-4 py-2 text-sm text-white" type="submit">
          Guardar cambios
        </button>
      </div>
      <div className="overflow-x-auto rounded-lg bg-white p-4 shadow-sm">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b">
              <th className="py-2 pr-2">Título</th>
              {MESES.map((m, idx) => (
                <th
                  key={m}
                  className={`px-1 text-center ${
                    anio === curso.anio && idx + 1 === curso.mes ? "text-rust" : ""
                  }`}
                >
                  {m}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {instrumentos.map((inst) => (
              <tr key={inst.id} className="border-b border-ink/10">
                <td className="whitespace-nowrap py-1 pr-2 font-medium">{inst.nombre}</td>
                {MESES.map((_, idx) => {
                  const mes = idx + 1;
                  const key = `${inst.id}-${mes}`;
                  const huecoMes =
                    inst.activo && anio === curso.anio && mes === curso.mes && valor(inst.id, mes) === "";
                  return (
                    <td key={mes}>
                      <input
                        className={`w-20 rounded border px-1 py-1 text-right ${
                          huecoMes ? "border-amber-400 bg-amber-50" : "border-ink/15"
                        }`}
                        value={valor(inst.id, mes)}
                        onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
                        inputMode="decimal"
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </form>
  );
}
