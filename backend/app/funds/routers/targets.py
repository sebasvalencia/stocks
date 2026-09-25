from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.funds.models import Fund, FundTarget, FundUnitValue
from app.funds.schemas import FundTargetIn, FundTargetOut, FundTargetProgressOut
from app.funds.services.target import current_target, last_unit_value, progress_pct

router = APIRouter(tags=["funds"])


def _out(row: FundTarget) -> FundTargetOut:
    return FundTargetOut(
        id=row.id,
        fund_id=row.fund_id,
        year=row.year,
        month=row.month,
        price=row.price,
        fund_name=row.fund.name if row.fund else None,
        fund_currency=row.fund.currency if row.fund else None,
    )


@router.get("/targets", response_model=list[FundTargetOut])
def list_targets(
    fund_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[FundTargetOut]:
    q = select(FundTarget).options(joinedload(FundTarget.fund))
    if fund_id is not None:
        q = q.where(FundTarget.fund_id == fund_id)
    rows = db.scalars(q.order_by(FundTarget.year.desc(), FundTarget.month.desc(), FundTarget.id.desc())).all()
    return [_out(r) for r in rows]


@router.put("/targets", response_model=FundTargetOut)
def upsert(body: FundTargetIn, db: Session = Depends(get_db)) -> FundTargetOut:
    fund = db.get(Fund, body.fund_id)
    if fund is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    row = db.scalar(
        select(FundTarget).where(
            FundTarget.fund_id == body.fund_id,
            FundTarget.year == body.year,
            FundTarget.month == body.month,
        )
    )
    if row is None:
        row = FundTarget(
            fund_id=body.fund_id,
            year=body.year,
            month=body.month,
            price=body.price,
        )
        db.add(row)
    else:
        row.price = body.price
    db.commit()
    db.refresh(row)
    row = db.scalar(
        select(FundTarget).options(joinedload(FundTarget.fund)).where(FundTarget.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(target_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(FundTarget, target_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_target_not_found")
    db.delete(row)
    db.commit()


@router.get("/target-progress", response_model=FundTargetProgressOut)
def progress(
    fund_id: int = Query(...),
    db: Session = Depends(get_db),
) -> FundTargetProgressOut:
    fund = db.get(Fund, fund_id)
    if fund is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fund_not_found")
    values = list(db.scalars(select(FundUnitValue).where(FundUnitValue.fund_id == fund_id)).all())
    targets = list(db.scalars(select(FundTarget).where(FundTarget.fund_id == fund_id)).all())
    latest = last_unit_value(values)
    current = current_target(targets)
    market = Decimal(latest.value) if latest else None
    target_price = Decimal(current.price) if current else None
    return FundTargetProgressOut(
        fund_id=fund.id,
        fund_name=fund.name,
        last_price=market,
        price_year=latest.year if latest else None,
        price_month=latest.month if latest else None,
        target=target_price,
        target_year=current.year if current else None,
        target_month=current.month if current else None,
        progress_pct=progress_pct(market, target_price),
        fund_currency=fund.currency,
    )
