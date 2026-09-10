from decimal import Decimal

from app.models import PrecioMensual


def mes_calendario_anterior(anio: int, mes: int) -> tuple[int, int]:
    if mes == 1:
        return anio - 1, 12
    return anio, mes - 1


def puntos_variacion(precios: list[PrecioMensual]) -> list[dict]:
    """Variación solo si existe el mes calendario anterior. No inventa huecos."""
    por_periodo = {(p.anio, p.mes): p.precio for p in precios}
    puntos: list[dict] = []
    for p in sorted(precios, key=lambda x: (x.anio, x.mes)):
        pa, pm = mes_calendario_anterior(p.anio, p.mes)
        prev = por_periodo.get((pa, pm))
        var = None
        if prev is not None and prev != 0:
            var = (Decimal(p.precio) - Decimal(prev)) / Decimal(prev) * Decimal(100)
        puntos.append(
            {
                "anio": p.anio,
                "mes": p.mes,
                "precio": Decimal(p.precio),
                "variacion_pct": var,
            }
        )
    return puntos
