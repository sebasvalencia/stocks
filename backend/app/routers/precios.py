from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Instrumento, PrecioMensual
from app.schemas import PrecioFaltanteOut, PrecioIn, PrecioOut, PreciosPendientesOut

router = APIRouter(prefix="/precios", tags=["precios"])


def _out(row: PrecioMensual) -> PrecioOut:
    return PrecioOut(
        id=row.id,
        instrumento_id=row.instrumento_id,
        anio=row.anio,
        mes=row.mes,
        precio=row.precio,
        instrumento_nombre=row.instrumento.nombre if row.instrumento else None,
    )


@router.get("/pendientes", response_model=PreciosPendientesOut)
def pendientes(
    anio: int = Query(..., ge=1900, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> PreciosPendientesOut:
    activos = list(
        db.scalars(select(Instrumento).where(Instrumento.activo.is_(True)).order_by(Instrumento.nombre)).all()
    )
    con_precio = {
        row.instrumento_id
        for row in db.scalars(
            select(PrecioMensual).where(PrecioMensual.anio == anio, PrecioMensual.mes == mes)
        ).all()
    }
    faltantes = [
        PrecioFaltanteOut(instrumento_id=i.id, instrumento_nombre=i.nombre)
        for i in activos
        if i.id not in con_precio
    ]
    return PreciosPendientesOut(
        anio=anio,
        mes=mes,
        total_activos=len(activos),
        pendientes=len(faltantes),
        faltantes=faltantes,
    )


@router.get("", response_model=list[PrecioOut])
def listar(
    anio: int | None = Query(default=None),
    instrumento_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PrecioOut]:
    q = select(PrecioMensual).options(joinedload(PrecioMensual.instrumento))
    if anio is not None:
        q = q.where(PrecioMensual.anio == anio)
    if instrumento_id is not None:
        q = q.where(PrecioMensual.instrumento_id == instrumento_id)
    rows = db.scalars(q.order_by(PrecioMensual.anio, PrecioMensual.mes)).all()
    return [_out(r) for r in rows]


@router.put("", response_model=PrecioOut)
def upsert(body: PrecioIn, db: Session = Depends(get_db)) -> PrecioOut:
    inst = db.get(Instrumento, body.instrumento_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    row = db.scalar(
        select(PrecioMensual).where(
            PrecioMensual.instrumento_id == body.instrumento_id,
            PrecioMensual.anio == body.anio,
            PrecioMensual.mes == body.mes,
        )
    )
    if row is None:
        row = PrecioMensual(
            instrumento_id=body.instrumento_id,
            anio=body.anio,
            mes=body.mes,
            precio=body.precio,
        )
        db.add(row)
    else:
        row.precio = body.precio
    db.commit()
    db.refresh(row)
    row = db.scalar(
        select(PrecioMensual)
        .options(joinedload(PrecioMensual.instrumento))
        .where(PrecioMensual.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/{precio_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(precio_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(PrecioMensual, precio_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Precio no encontrado")
    db.delete(row)
    db.commit()
