import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type PreciosPendientes } from "./api";

const MESES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

export function mesCurso(): { anio: number; mes: number } {
  const hoy = new Date();
  return { anio: hoy.getFullYear(), mes: hoy.getMonth() + 1 };
}

type Props = {
  enlace?: boolean;
  recargar?: number;
};

export default function BannerPrecios({ enlace = false, recargar = 0 }: Props) {
  const { anio, mes } = mesCurso();
  const [data, setData] = useState<PreciosPendientes | null>(null);

  useEffect(() => {
    api.preciosPendientes(anio, mes).then(setData).catch(() => setData(null));
  }, [anio, mes, recargar]);

  if (!data || data.pendientes === 0) return null;

  const nombres = data.faltantes.map((f) => f.instrumento_nombre).join(", ");
  const texto =
    data.pendientes === 1
      ? `Falta 1 precio de ${MESES[mes - 1]} (${data.total_activos} títulos activos).`
      : `Faltan ${data.pendientes} precios de ${MESES[mes - 1]} (${data.total_activos} títulos activos).`;

  return (
    <p className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-950">
      {texto} {nombres}.
      {enlace && (
        <>
          {" "}
          <Link to="/precios" className="underline">
            Cargar en Precios
          </Link>
        </>
      )}
    </p>
  );
}
