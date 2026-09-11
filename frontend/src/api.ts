export type Corredor = { id: number; nombre: string };
export type Instrumento = { id: number; nombre: string; activo: boolean };
export type Movimiento = {
  id: number;
  instrumento_id: number;
  corredor_id: number;
  tipo: "compra" | "venta";
  anio: number;
  mes: number | null;
  cantidad: string;
  comision: string;
  instrumento_nombre: string | null;
  corredor_nombre: string | null;
};
export type Precio = {
  id: number;
  instrumento_id: number;
  anio: number;
  mes: number;
  precio: string;
  instrumento_nombre: string | null;
};
export type Posicion = {
  instrumento_id: number;
  instrumento_nombre: string;
  corredor_id: number;
  corredor_nombre: string;
  saldo: string;
  precio_ultimo: string | null;
  anio_precio: number | null;
  mes_precio: number | null;
  valor: string | null;
  peso_pct: string | null;
  sin_precio: boolean;
};
export type Resumen = { total: string; posiciones: Posicion[] };
export type MovimientoPayload = {
  instrumento_id: number;
  corredor_id: number;
  tipo: "compra" | "venta";
  anio: number;
  mes: number | null;
  cantidad: number;
  comision: number;
};
export type Objetivo = {
  id: number;
  instrumento_id: number;
  anio: number;
  mes: number;
  precio: string;
  instrumento_nombre: string | null;
};
export type AvanceObjetivo = {
  instrumento_id: number;
  instrumento_nombre: string;
  precio_ultimo: string | null;
  anio_precio: number | null;
  mes_precio: number | null;
  objetivo: string | null;
  anio_objetivo: number | null;
  mes_objetivo: number | null;
  avance_pct: string | null;
};
export type Variacion = {
  instrumento_id: number;
  instrumento_nombre: string;
  puntos: {
    anio: number;
    mes: number;
    precio: string;
    variacion_pct: string | null;
  }[];
};

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
      else if (Array.isArray(body.detail)) msg = body.detail.map((d: { msg?: string }) => d.msg).join("; ");
    } catch {
      /* keep statusText */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ status: string }>("/health"),
  corredores: () => req<Corredor[]>("/corredores"),
  crearCorredor: (nombre: string) =>
    req<Corredor>("/corredores", { method: "POST", body: JSON.stringify({ nombre }) }),
  instrumentos: () => req<Instrumento[]>("/instrumentos"),
  crearInstrumento: (nombre: string) =>
    req<Instrumento>("/instrumentos", { method: "POST", body: JSON.stringify({ nombre, activo: true }) }),
  patchInstrumento: (id: number, body: { activo?: boolean; nombre?: string }) =>
    req<Instrumento>(`/instrumentos/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  movimientos: () => req<Movimiento[]>("/movimientos"),
  crearMovimiento: (body: MovimientoPayload) =>
    req<Movimiento>("/movimientos", { method: "POST", body: JSON.stringify(body) }),
  actualizarMovimiento: (id: number, body: MovimientoPayload) =>
    req<Movimiento>(`/movimientos/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  borrarMovimiento: (id: number) => req<void>(`/movimientos/${id}`, { method: "DELETE" }),
  precios: (anio?: number) => req<Precio[]>(anio ? `/precios?anio=${anio}` : "/precios"),
  upsertPrecio: (body: { instrumento_id: number; anio: number; mes: number; precio: number }) =>
    req<Precio>("/precios", { method: "PUT", body: JSON.stringify(body) }),
  resumen: () => req<Resumen>("/resumen"),
  variacion: (instrumentoId: number) =>
    req<Variacion>(`/variacion-precios?instrumento_id=${instrumentoId}`),
  objetivos: (instrumentoId: number) =>
    req<Objetivo[]>(`/objetivos?instrumento_id=${instrumentoId}`),
  upsertObjetivo: (body: { instrumento_id: number; anio: number; mes: number; precio: number }) =>
    req<Objetivo>("/objetivos", { method: "PUT", body: JSON.stringify(body) }),
  avanceObjetivo: (instrumentoId: number) =>
    req<AvanceObjetivo>(`/avance-objetivo?instrumento_id=${instrumentoId}`),
};
