from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.funds.models import Fiduciary, FundTrade
from app.funds.schemas import FiduciaryIn, FiduciaryOut

router = APIRouter(prefix="/fiduciaries", tags=["funds"])


@router.get("", response_model=list[FiduciaryOut])
def list_fiduciaries(db: Session = Depends(get_db)) -> list[Fiduciary]:
    return list(db.scalars(select(Fiduciary).order_by(Fiduciary.name)).all())


@router.get("/{fiduciary_id}", response_model=FiduciaryOut)
def get_one(fiduciary_id: int, db: Session = Depends(get_db)) -> Fiduciary:
    row = db.get(Fiduciary, fiduciary_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fiduciary_not_found")
    return row


@router.post("", response_model=FiduciaryOut, status_code=status.HTTP_201_CREATED)
def create(body: FiduciaryIn, db: Session = Depends(get_db)) -> Fiduciary:
    row = Fiduciary(name=body.name.strip())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "fiduciary_exists")
    db.refresh(row)
    return row


@router.put("/{fiduciary_id}", response_model=FiduciaryOut)
def update(fiduciary_id: int, body: FiduciaryIn, db: Session = Depends(get_db)) -> Fiduciary:
    row = db.get(Fiduciary, fiduciary_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fiduciary_not_found")
    row.name = body.name.strip()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "fiduciary_exists")
    db.refresh(row)
    return row


@router.delete("/{fiduciary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(fiduciary_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Fiduciary, fiduciary_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fiduciary_not_found")
    if db.scalar(select(FundTrade.id).where(FundTrade.fiduciary_id == fiduciary_id).limit(1)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_fiduciary")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_fiduciary")
