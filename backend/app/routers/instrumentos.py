from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Instrumento
from app.schemas import InstrumentoIn, InstrumentoOut, InstrumentoUpdate
from app.services.reglas import validar_inactivar

router = APIRouter(prefix="/instrumentos", tags=["instrumentos"])


@router.get("", response_model=list[InstrumentoOut])
def listar(db: Session = Depends(get_db)) -> list[Instrumento]:
    return list(db.scalars(select(Instrumento).order_by(Instrumento.nombre)).all())


@router.get("/{instrumento_id}", response_model=InstrumentoOut)
def obtener(instrumento_id: int, db: Session = Depends(get_db)) -> Instrumento:
    row = db.get(Instrumento, instrumento_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    return row


@router.post("", response_model=InstrumentoOut, status_code=status.HTTP_201_CREATED)
def crear(body: InstrumentoIn, db: Session = Depends(get_db)) -> Instrumento:
    row = Instrumento(nombre=body.nombre.strip(), activo=body.activo)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un título con ese nombre")
    db.refresh(row)
    return row


@router.put("/{instrumento_id}", response_model=InstrumentoOut)
def actualizar(
    instrumento_id: int, body: InstrumentoUpdate, db: Session = Depends(get_db)
) -> Instrumento:
    row = db.get(Instrumento, instrumento_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    if body.activo is not None:
        validar_inactivar(db, row, body.activo)
        row.activo = body.activo
    if body.nombre is not None:
        row.nombre = body.nombre.strip()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un título con ese nombre")
    db.refresh(row)
    return row


@router.delete("/{instrumento_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(instrumento_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Instrumento, instrumento_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede borrar: hay movimientos o precios de este título",
        )
