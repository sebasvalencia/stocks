import { FormEvent, useEffect, useState } from "react";
import { api, type Corredor, type Instrumento } from "../api";

export default function Catalogo() {
  const [instrumentos, setInstrumentos] = useState<Instrumento[]>([]);
  const [corredores, setCorredores] = useState<Corredor[]>([]);
  const [nombreTitulo, setNombreTitulo] = useState("");
  const [nombreCorredor, setNombreCorredor] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function cargar() {
    const [i, c] = await Promise.all([api.instrumentos(), api.corredores()]);
    setInstrumentos(i);
    setCorredores(c);
  }

  useEffect(() => {
    cargar().catch((e: Error) => setError(e.message));
  }, []);

  async function altaTitulo(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.crearInstrumento(nombreTitulo.trim());
      setNombreTitulo("");
      await cargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  async function altaCorredor(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await api.crearCorredor(nombreCorredor.trim());
      setNombreCorredor("");
      await cargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  async function toggleActivo(row: Instrumento) {
    setError(null);
    try {
      await api.patchInstrumento(row.id, { activo: !row.activo });
      await cargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <div className="grid gap-8 md:grid-cols-2">
      {error && (
        <p className="md:col-span-2 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </p>
      )}
      <section className="rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">Títulos</h2>
        <form onSubmit={altaTitulo} className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-ink/20 px-3 py-2"
            value={nombreTitulo}
            onChange={(e) => setNombreTitulo(e.target.value)}
            placeholder="Nombre"
            required
          />
          <button className="rounded bg-moss px-3 py-2 text-sm text-white" type="submit">
            Agregar
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {instrumentos.map((row) => (
            <li key={row.id} className="flex items-center justify-between py-2">
              <span>
                {row.nombre}{" "}
                <span className="text-xs text-ink/50">{row.activo ? "activo" : "inactivo"}</span>
              </span>
              <button
                type="button"
                className="text-sm text-rust underline"
                onClick={() => toggleActivo(row)}
              >
                {row.activo ? "Inactivar" : "Activar"}
              </button>
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-lg bg-white p-4 shadow-sm">
        <h2 className="font-display text-xl">Corredores</h2>
        <form onSubmit={altaCorredor} className="mt-3 flex gap-2">
          <input
            className="flex-1 rounded border border-ink/20 px-3 py-2"
            value={nombreCorredor}
            onChange={(e) => setNombreCorredor(e.target.value)}
            placeholder="Nombre"
            required
          />
          <button className="rounded bg-moss px-3 py-2 text-sm text-white" type="submit">
            Agregar
          </button>
        </form>
        <ul className="mt-4 divide-y">
          {corredores.map((row) => (
            <li key={row.id} className="py-2">
              {row.nombre}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
