import { FormEvent, useEffect, useState } from "react";
import { api, type Corredor, type Instrumento, type Movimiento } from "../api";

export default function Movimientos() {
  const [instrumentos, setInstrumentos] = useState<Instrumento[]>([]);
  const [corredores, setCorredores] = useState<Corredor[]>([]);
  const [rows, setRows] = useState<Movimiento[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [instrumentoId, setInstrumentoId] = useState("");
  const [corredorId, setCorredorId] = useState("");
  const [tipo, setTipo] = useState<"compra" | "venta">("compra");
  const [anio, setAnio] = useState("2026");
  const [mes, setMes] = useState("");
  const [cantidad, setCantidad] = useState("");
  const [comision, setComision] = useState("0");

  async function cargar() {
    const [i, c, m] = await Promise.all([api.instrumentos(), api.corredores(), api.movimientos()]);
    setInstrumentos(i);
    setCorredores(c);
    setRows(m);
  }

  useEffect(() => {
    cargar().catch((e: Error) => setError(e.message));
  }, []);

  function limpiarFormulario() {
    setEditandoId(null);
    setInstrumentoId("");
    setCorredorId("");
    setTipo("compra");
    setAnio("2026");
    setMes("");
    setCantidad("");
    setComision("0");
  }

  function payload() {
    return {
      instrumento_id: Number(instrumentoId),
      corredor_id: Number(corredorId),
      tipo,
      anio: Number(anio),
      mes: mes === "" ? null : Number(mes),
      cantidad: Number(cantidad),
      comision: comision === "" ? 0 : Number(comision),
    };
  }

  function editar(row: Movimiento) {
    setError(null);
    setEditandoId(row.id);
    setInstrumentoId(String(row.instrumento_id));
    setCorredorId(String(row.corredor_id));
    setTipo(row.tipo);
    setAnio(String(row.anio));
    setMes(row.mes == null ? "" : String(row.mes));
    setCantidad(String(Number(row.cantidad)));
    setComision(String(Number(row.comision)));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (editandoId == null) {
        await api.crearMovimiento(payload());
      } else {
        await api.actualizarMovimiento(editandoId, payload());
      }
      limpiarFormulario();
      await cargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  async function borrar(row: Movimiento) {
    if (
      !window.confirm(
        `¿Borrar ${row.tipo} de ${row.instrumento_nombre} en ${row.corredor_nombre}?`,
      )
    ) {
      return;
    }
    setError(null);
    try {
      await api.borrarMovimiento(row.id);
      if (editandoId === row.id) limpiarFormulario();
      await cargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <div className="space-y-6">
      {error && (
        <p className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}
      <section className="rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">
          {editandoId == null ? "Registrar compra o venta" : "Editar movimiento"}
        </h2>
        <form onSubmit={onSubmit} className="mt-4 grid gap-3 sm:grid-cols-3">
          <label className="text-sm">
            Título
            <select
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              value={instrumentoId}
              onChange={(e) => setInstrumentoId(e.target.value)}
              required
            >
              <option value="">Seleccione</option>
              {instrumentos.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.nombre}
                  {i.activo ? "" : " (inactivo)"}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            Corredor
            <select
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              value={corredorId}
              onChange={(e) => setCorredorId(e.target.value)}
              required
            >
              <option value="">Seleccione</option>
              {corredores.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nombre}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            Tipo
            <select
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              value={tipo}
              onChange={(e) => setTipo(e.target.value as "compra" | "venta")}
            >
              <option value="compra">Compra</option>
              <option value="venta">Venta</option>
            </select>
          </label>
          <label className="text-sm">
            Año
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              value={anio}
              onChange={(e) => setAnio(e.target.value)}
              required
            />
          </label>
          <label className="text-sm">
            Mes (opcional)
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              min={1}
              max={12}
              value={mes}
              onChange={(e) => setMes(e.target.value)}
              placeholder="—"
            />
          </label>
          <label className="text-sm">
            Cantidad
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              min={0.000001}
              step="any"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
              required
            />
          </label>
          <label className="text-sm">
            Comisión (COP)
            <input
              className="mt-1 w-full rounded border border-ink/20 px-2 py-2"
              type="number"
              min={0}
              step="any"
              value={comision}
              onChange={(e) => setComision(e.target.value)}
            />
          </label>
          <div className="flex gap-2 sm:col-span-3">
            <button className="rounded bg-rust px-4 py-2 text-sm text-white" type="submit">
              {editandoId == null ? "Guardar" : "Guardar cambios"}
            </button>
            {editandoId != null && (
              <button
                className="rounded border border-ink/20 px-4 py-2 text-sm"
                type="button"
                onClick={limpiarFormulario}
              >
                Cancelar
              </button>
            )}
          </div>
        </form>
      </section>
      <section className="overflow-x-auto rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">Historial</h2>
        <table className="mt-3 w-full text-left text-sm">
          <thead>
            <tr className="border-b text-ink/60">
              <th className="py-2">Año</th>
              <th>Mes</th>
              <th>Título</th>
              <th>Corredor</th>
              <th>Tipo</th>
              <th className="text-right">Cantidad</th>
              <th className="text-right">Comisión</th>
              <th className="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b border-ink/10">
                <td className="py-2">{r.anio}</td>
                <td>{r.mes ?? "—"}</td>
                <td>{r.instrumento_nombre}</td>
                <td>{r.corredor_nombre}</td>
                <td>{r.tipo}</td>
                <td className="text-right">{Number(r.cantidad).toLocaleString("es-CO")}</td>
                <td className="text-right">
                  {Number(r.comision).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 })}
                </td>
                <td className="space-x-3 text-right">
                  <button type="button" className="text-rust underline" onClick={() => editar(r)}>
                    Editar
                  </button>
                  <button type="button" className="text-ink/60 underline" onClick={() => borrar(r)}>
                    Borrar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
