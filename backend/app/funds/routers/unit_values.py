from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.funds.models import Fund, FundUnitValue
from app.funds.schemas import MissingUnitValueOut, PendingUnitValuesOut, UnitValueIn, UnitValueOut

router = APIRouter(prefix="/unit-values", tags=["funds"])


def _out(row: FundUnitValue) -> UnitValueOut:
    return UnitValueOut(
        id=row.id,
        fund_id=row.fund_id,
        year=row.year,
        month=row.month,
        value=row.value,
        fund_name=row.fund.name if row.fund else None,
        fund_currency=row.fund.currency if row.fund else None,
    )


@router.get("/pending", response_model=PendingUnitValuesOut)
def pending(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> PendingUnitValuesOut:
    active = list(db.scalars(select(Fund).where(Fund.active.is_(True)).order_by(Fund.name)).all())
    with_value = {
        row.fund_id
        for row in db.scalars(
            select(FundUnitValue).where(FundUnitValue.year == year, FundUnitValue.month == month)
        ).all()
    }
    missing = [
        MissingUnitValueOut(fund_id=f.id, fund_name=f.name) for f in active if f.id not in with_value
    ]
    return PendingUnitValuesOut(
        year=year,
        month=month,
        total_active=len(active),
        pending=len(missing),
        missing=missing,
    )


@router.get("", response_model=list[UnitValueOut])
def list_unit_values(
    year: int | None = Query(default=None),
    fund_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[UnitValueOut]:
    q = select(FundUnitValue).options(joinedload(FundUnitValue.fund))
    if year is not None:
        q = q.where(FundUnitValue.year == year)
    if fund_id is not None:
        q = q.where(FundUnitValue.fund_id == fund_id)
    rows = db.scalars(q.order_by(FundUnitValue.year, FundUnitValue.month)).all()
    return [_out(r) for r in rows]


@router.put("", response_model=UnitValueOut)
def upsert(body: UnitValueIn, db: Session = Depends(get_db)) -> UnitValueOut:
    fund = db.get(Fund, body.fund_id)
    if fund is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    row = db.scalar(
        select(FundUnitValue).where(
            FundUnitValue.fund_id == body.fund_id,
            FundUnitValue.year == body.year,
            FundUnitValue.month == body.month,
        )
    )
    if row is None:
        row = FundUnitValue(
            fund_id=body.fund_id,
            year=body.year,
            month=body.month,
            value=body.value,
        )
        db.add(row)
    else:
        row.value = body.value
    db.commit()
    db.refresh(row)
    row = db.scalar(
        select(FundUnitValue)
        .options(joinedload(FundUnitValue.fund))
        .where(FundUnitValue.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/{value_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(value_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(FundUnitValue, value_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "unit_value_not_found")
    db.delete(row)
    db.commit()
