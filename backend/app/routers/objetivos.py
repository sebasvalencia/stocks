from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Instrumento, ObjetivoPrecio, PrecioMensual
from app.schemas import AvanceObjetivoOut, ObjetivoIn, ObjetivoOut
from app.services.objetivo import avance_pct, objetivo_vigente, ultimo_precio

router = APIRouter(tags=["objetivos"])


def _out(row: ObjetivoPrecio) -> ObjetivoOut:
    return ObjetivoOut(
        id=row.id,
        instrumento_id=row.instrumento_id,
        anio=row.anio,
        mes=row.mes,
        precio=row.precio,
        instrumento_nombre=row.instrumento.nombre if row.instrumento else None,
    )


@router.get("/objetivos", response_model=list[ObjetivoOut])
def listar(
    instrumento_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ObjetivoOut]:
    q = select(ObjetivoPrecio).options(joinedload(ObjetivoPrecio.instrumento))
    if instrumento_id is not None:
        q = q.where(ObjetivoPrecio.instrumento_id == instrumento_id)
    rows = db.scalars(
        q.order_by(ObjetivoPrecio.anio.desc(), ObjetivoPrecio.mes.desc(), ObjetivoPrecio.id.desc())
    ).all()
    return [_out(r) for r in rows]


@router.put("/objetivos", response_model=ObjetivoOut)
def upsert(body: ObjetivoIn, db: Session = Depends(get_db)) -> ObjetivoOut:
    inst = db.get(Instrumento, body.instrumento_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    row = db.scalar(
        select(ObjetivoPrecio).where(
            ObjetivoPrecio.instrumento_id == body.instrumento_id,
            ObjetivoPrecio.anio == body.anio,
            ObjetivoPrecio.mes == body.mes,
        )
    )
    if row is None:
        row = ObjetivoPrecio(
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
        select(ObjetivoPrecio)
        .options(joinedload(ObjetivoPrecio.instrumento))
        .where(ObjetivoPrecio.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/objetivos/{objetivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(objetivo_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(ObjetivoPrecio, objetivo_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Objetivo no encontrado")
    db.delete(row)
    db.commit()


@router.get("/avance-objetivo", response_model=AvanceObjetivoOut)
def avance(
    instrumento_id: int = Query(...),
    db: Session = Depends(get_db),
) -> AvanceObjetivoOut:
    inst = db.get(Instrumento, instrumento_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    precios = list(
        db.scalars(select(PrecioMensual).where(PrecioMensual.instrumento_id == instrumento_id)).all()
    )
    objetivos = list(
        db.scalars(select(ObjetivoPrecio).where(ObjetivoPrecio.instrumento_id == instrumento_id)).all()
    )
    ultimo = ultimo_precio(precios)
    vigente = objetivo_vigente(objetivos)
    precio_mkt = Decimal(ultimo.precio) if ultimo else None
    precio_obj = Decimal(vigente.precio) if vigente else None
    return AvanceObjetivoOut(
        instrumento_id=inst.id,
        instrumento_nombre=inst.nombre,
        precio_ultimo=precio_mkt,
        anio_precio=ultimo.anio if ultimo else None,
        mes_precio=ultimo.mes if ultimo else None,
        objetivo=precio_obj,
        anio_objetivo=vigente.anio if vigente else None,
        mes_objetivo=vigente.mes if vigente else None,
        avance_pct=avance_pct(precio_mkt, precio_obj),
    )
