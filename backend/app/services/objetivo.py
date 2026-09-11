from decimal import Decimal

from app.models import ObjetivoPrecio, PrecioMensual


def objetivo_vigente(objetivos: list[ObjetivoPrecio]) -> ObjetivoPrecio | None:
    if not objetivos:
        return None
    return max(objetivos, key=lambda o: (o.anio, o.mes, o.id))


def avance_pct(precio_ultimo: Decimal | None, objetivo: Decimal | None) -> Decimal | None:
    if precio_ultimo is None or objetivo is None or objetivo == 0:
        return None
    return (Decimal(precio_ultimo) / Decimal(objetivo)) * Decimal(100)


def ultimo_precio(precios: list[PrecioMensual]) -> PrecioMensual | None:
    if not precios:
        return None
    return max(precios, key=lambda p: (p.anio, p.mes))
