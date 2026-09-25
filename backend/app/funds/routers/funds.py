from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.funds.models import Fund, FundTarget, FundTrade, FundUnitValue
from app.funds.schemas import FundIn, FundOut, FundUpdate
from app.funds.services.rules import validate_currency_change, validate_inactivate

router = APIRouter(prefix="/funds", tags=["funds"])


@router.get("", response_model=list[FundOut])
def list_funds(db: Session = Depends(get_db)) -> list[Fund]:
    return list(db.scalars(select(Fund).order_by(Fund.name)).all())


@router.get("/{fund_id}", response_model=FundOut)
def get_one(fund_id: int, db: Session = Depends(get_db)) -> Fund:
    row = db.get(Fund, fund_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    return row


@router.post("", response_model=FundOut, status_code=status.HTTP_201_CREATED)
def create(body: FundIn, db: Session = Depends(get_db)) -> Fund:
    row = Fund(name=body.name.strip(), active=body.active, currency=body.currency)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "fund_exists")
    db.refresh(row)
    return row


@router.put("/{fund_id}", response_model=FundOut)
def update(fund_id: int, body: FundUpdate, db: Session = Depends(get_db)) -> Fund:
    row = db.get(Fund, fund_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    if body.active is not None:
        validate_inactivate(db, row, body.active)
        row.active = body.active
    if body.name is not None:
        row.name = body.name.strip()
    if body.currency is not None:
        validate_currency_change(db, row, body.currency)
        row.currency = body.currency
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "fund_exists")
    db.refresh(row)
    return row


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(fund_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Fund, fund_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    has_data = (
        db.scalar(select(FundTrade.id).where(FundTrade.fund_id == fund_id).limit(1)) is not None
        or db.scalar(select(FundUnitValue.id).where(FundUnitValue.fund_id == fund_id).limit(1)) is not None
        or db.scalar(select(FundTarget.id).where(FundTarget.fund_id == fund_id).limit(1)) is not None
    )
    if has_data:
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_fund")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_fund")
