from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Corredor, Instrumento, Movimiento, PrecioMensual
from app.schemas import PosicionOut, ResumenOut, SaldoOut, VariacionOut, VariacionPuntoOut
from app.services.saldos import saldo_par
from app.services.variacion import puntos_variacion

router = APIRouter(tags=["resumen"])


def _ultimo_precio(precios: list[PrecioMensual]) -> PrecioMensual | None:
    if not precios:
        return None
    return max(precios, key=lambda p: (p.anio, p.mes))


@router.get("/saldos", response_model=list[SaldoOut])
def saldos(db: Session = Depends(get_db)) -> list[SaldoOut]:
    pares = db.execute(
        select(Movimiento.instrumento_id, Movimiento.corredor_id).distinct()
    ).all()
    out: list[SaldoOut] = []
    for instrumento_id, corredor_id in pares:
        inst = db.get(Instrumento, instrumento_id)
        corr = db.get(Corredor, corredor_id)
        if inst is None or corr is None:
            continue
        out.append(
            SaldoOut(
                instrumento_id=inst.id,
                instrumento_nombre=inst.nombre,
                corredor_id=corr.id,
                corredor_nombre=corr.nombre,
                activo=inst.activo,
                saldo=saldo_par(db, inst.id, corr.id),
            )
        )
    out.sort(key=lambda r: (r.instrumento_nombre, r.corredor_nombre))
    return out


@router.get("/resumen", response_model=ResumenOut)
def resumen(db: Session = Depends(get_db)) -> ResumenOut:
    pares = db.execute(
        select(Movimiento.instrumento_id, Movimiento.corredor_id).distinct()
    ).all()
    precios_por_inst: dict[int, list[PrecioMensual]] = defaultdict(list)
    for p in db.scalars(select(PrecioMensual)).all():
        precios_por_inst[p.instrumento_id].append(p)

    posiciones: list[PosicionOut] = []
    for instrumento_id, corredor_id in pares:
        inst = db.get(Instrumento, instrumento_id)
        corr = db.get(Corredor, corredor_id)
        if inst is None or corr is None or not inst.activo:
            continue
        saldo = saldo_par(db, inst.id, corr.id)
        ultimo = _ultimo_precio(precios_por_inst.get(inst.id, []))
        sin_precio = ultimo is None
        valor = None
        if ultimo is not None:
            valor = saldo * Decimal(ultimo.precio)
        posiciones.append(
            PosicionOut(
                instrumento_id=inst.id,
                instrumento_nombre=inst.nombre,
                corredor_id=corr.id,
                corredor_nombre=corr.nombre,
                saldo=saldo,
                precio_ultimo=Decimal(ultimo.precio) if ultimo else None,
                anio_precio=ultimo.anio if ultimo else None,
                mes_precio=ultimo.mes if ultimo else None,
                valor=valor,
                peso_pct=None,
                sin_precio=sin_precio,
            )
        )

    total = sum((p.valor for p in posiciones if p.valor is not None), Decimal(0))
    for p in posiciones:
        if p.valor is not None and total > 0:
            p.peso_pct = (p.valor / total) * Decimal(100)
        elif p.valor is not None:
            p.peso_pct = Decimal(0)

    posiciones.sort(key=lambda r: (-float(r.valor or 0), r.instrumento_nombre))
    return ResumenOut(total=total, posiciones=posiciones)


@router.get("/variacion-precios", response_model=VariacionOut)
def variacion(
    instrumento_id: int = Query(...),
    db: Session = Depends(get_db),
) -> VariacionOut:
    inst = db.get(Instrumento, instrumento_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    precios = list(
        db.scalars(
            select(PrecioMensual)
            .where(PrecioMensual.instrumento_id == instrumento_id)
            .options(joinedload(PrecioMensual.instrumento))
        ).all()
    )
    puntos = [
        VariacionPuntoOut(
            anio=p["anio"],
            mes=p["mes"],
            precio=p["precio"],
            variacion_pct=p["variacion_pct"],
        )
        for p in puntos_variacion(precios)
    ]
    return VariacionOut(
        instrumento_id=inst.id,
        instrumento_nombre=inst.nombre,
        puntos=puntos,
    )
