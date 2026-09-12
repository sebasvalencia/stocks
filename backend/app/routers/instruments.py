from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Instrument
from app.schemas import InstrumentIn, InstrumentOut, InstrumentUpdate
from app.services.rules import validate_inactivate

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("", response_model=list[InstrumentOut])
def list_instruments(db: Session = Depends(get_db)) -> list[Instrument]:
    return list(db.scalars(select(Instrument).order_by(Instrument.name)).all())


@router.get("/{instrument_id}", response_model=InstrumentOut)
def get_one(instrument_id: int, db: Session = Depends(get_db)) -> Instrument:
    row = db.get(Instrument, instrument_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    return row


@router.post("", response_model=InstrumentOut, status_code=status.HTTP_201_CREATED)
def create(body: InstrumentIn, db: Session = Depends(get_db)) -> Instrument:
    row = Instrument(name=body.name.strip(), active=body.active)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "instrument_exists")
    db.refresh(row)
    return row


@router.put("/{instrument_id}", response_model=InstrumentOut)
def update(
    instrument_id: int, body: InstrumentUpdate, db: Session = Depends(get_db)
) -> Instrument:
    row = db.get(Instrument, instrument_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    if body.active is not None:
        validate_inactivate(db, row, body.active)
        row.active = body.active
    if body.name is not None:
        row.name = body.name.strip()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "instrument_exists")
    db.refresh(row)
    return row


@router.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(instrument_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Instrument, instrument_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_instrument")
