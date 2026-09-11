from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Movimiento
from app.schemas import MovimientoIn, MovimientoOut
from app.services.reglas import get_movimiento, validar_movimiento
from app.services.saldos import saldo_par

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


def _out(row: Movimiento) -> MovimientoOut:
    return MovimientoOut(
        id=row.id,
        instrumento_id=row.instrumento_id,
        corredor_id=row.corredor_id,
        tipo=row.tipo,
        anio=row.anio,
        mes=row.mes,
        cantidad=row.cantidad,
        comision=row.comision,
        instrumento_nombre=row.instrumento.nombre if row.instrumento else None,
        corredor_nombre=row.corredor.nombre if row.corredor else None,
    )


@router.get("", response_model=list[MovimientoOut])
def listar(db: Session = Depends(get_db)) -> list[MovimientoOut]:
    rows = db.scalars(
        select(Movimiento)
        .options(joinedload(Movimiento.instrumento), joinedload(Movimiento.corredor))
        .order_by(Movimiento.anio.desc(), Movimiento.id.desc())
    ).all()
    return [_out(r) for r in rows]


@router.get("/{movimiento_id}", response_model=MovimientoOut)
def obtener(movimiento_id: int, db: Session = Depends(get_db)) -> MovimientoOut:
    row = get_movimiento(db, movimiento_id)
    return _out(row)


@router.post("", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def crear(body: MovimientoIn, db: Session = Depends(get_db)) -> MovimientoOut:
    validar_movimiento(
        db,
        instrumento_id=body.instrumento_id,
        corredor_id=body.corredor_id,
        tipo=body.tipo,
        cantidad=body.cantidad,
    )
    row = Movimiento(
        instrumento_id=body.instrumento_id,
        corredor_id=body.corredor_id,
        tipo=body.tipo,
        anio=body.anio,
        mes=body.mes,
        cantidad=body.cantidad,
        comision=body.comision,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    row = get_movimiento(db, row.id)
    return _out(row)


@router.put("/{movimiento_id}", response_model=MovimientoOut)
def actualizar(
    movimiento_id: int, body: MovimientoIn, db: Session = Depends(get_db)
) -> MovimientoOut:
    row = get_movimiento(db, movimiento_id)
    validar_movimiento(
        db,
        instrumento_id=body.instrumento_id,
        corredor_id=body.corredor_id,
        tipo=body.tipo,
        cantidad=body.cantidad,
        exclude_id=row.id,
    )
    row.instrumento_id = body.instrumento_id
    row.corredor_id = body.corredor_id
    row.tipo = body.tipo
    row.anio = body.anio
    row.mes = body.mes
    row.cantidad = body.cantidad
    row.comision = body.comision
    db.commit()
    db.refresh(row)
    row = get_movimiento(db, row.id)
    return _out(row)


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(movimiento_id: int, db: Session = Depends(get_db)) -> None:
    row = get_movimiento(db, movimiento_id)
    restante = saldo_par(db, row.instrumento_id, row.corredor_id, exclude_id=row.id)
    if restante < 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No se puede borrar: el saldo del corredor quedaría negativo",
        )
    db.delete(row)
    db.commit()
