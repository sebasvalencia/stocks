from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Corredor
from app.schemas import CorredorIn, CorredorOut

router = APIRouter(prefix="/corredores", tags=["corredores"])


@router.get("", response_model=list[CorredorOut])
def listar(db: Session = Depends(get_db)) -> list[Corredor]:
    return list(db.scalars(select(Corredor).order_by(Corredor.nombre)).all())


@router.get("/{corredor_id}", response_model=CorredorOut)
def obtener(corredor_id: int, db: Session = Depends(get_db)) -> Corredor:
    row = db.get(Corredor, corredor_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corredor no encontrado")
    return row


@router.post("", response_model=CorredorOut, status_code=status.HTTP_201_CREATED)
def crear(body: CorredorIn, db: Session = Depends(get_db)) -> Corredor:
    row = Corredor(nombre=body.nombre.strip())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un corredor con ese nombre")
    db.refresh(row)
    return row


@router.put("/{corredor_id}", response_model=CorredorOut)
def actualizar(corredor_id: int, body: CorredorIn, db: Session = Depends(get_db)) -> Corredor:
    row = db.get(Corredor, corredor_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corredor no encontrado")
    row.nombre = body.nombre.strip()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un corredor con ese nombre")
    db.refresh(row)
    return row


@router.delete("/{corredor_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(corredor_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Corredor, corredor_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corredor no encontrado")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede borrar: hay movimientos con este corredor",
        )
