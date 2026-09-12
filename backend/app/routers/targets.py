from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Instrument, MonthlyPrice, PriceTarget
from app.schemas import TargetIn, TargetOut, TargetProgressOut
from app.services.target import current_target, last_price, progress_pct

router = APIRouter(tags=["targets"])


def _out(row: PriceTarget) -> TargetOut:
    return TargetOut(
        id=row.id,
        instrument_id=row.instrument_id,
        year=row.year,
        month=row.month,
        price=row.price,
        instrument_name=row.instrument.name if row.instrument else None,
    )


@router.get("/targets", response_model=list[TargetOut])
def list_targets(
    instrument_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[TargetOut]:
    q = select(PriceTarget).options(joinedload(PriceTarget.instrument))
    if instrument_id is not None:
        q = q.where(PriceTarget.instrument_id == instrument_id)
    rows = db.scalars(
        q.order_by(PriceTarget.year.desc(), PriceTarget.month.desc(), PriceTarget.id.desc())
    ).all()
    return [_out(r) for r in rows]


@router.put("/targets", response_model=TargetOut)
def upsert(body: TargetIn, db: Session = Depends(get_db)) -> TargetOut:
    inst = db.get(Instrument, body.instrument_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    row = db.scalar(
        select(PriceTarget).where(
            PriceTarget.instrument_id == body.instrument_id,
            PriceTarget.year == body.year,
            PriceTarget.month == body.month,
        )
    )
    if row is None:
        row = PriceTarget(
            instrument_id=body.instrument_id,
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
        select(PriceTarget)
        .options(joinedload(PriceTarget.instrument))
        .where(PriceTarget.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(target_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(PriceTarget, target_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "target_not_found")
    db.delete(row)
    db.commit()


@router.get("/target-progress", response_model=TargetProgressOut)
def progress(
    instrument_id: int = Query(...),
    db: Session = Depends(get_db),
) -> TargetProgressOut:
    inst = db.get(Instrument, instrument_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    prices = list(
        db.scalars(select(MonthlyPrice).where(MonthlyPrice.instrument_id == instrument_id)).all()
    )
    targets = list(
        db.scalars(select(PriceTarget).where(PriceTarget.instrument_id == instrument_id)).all()
    )
    latest = last_price(prices)
    current = current_target(targets)
    market = Decimal(latest.price) if latest else None
    target_price = Decimal(current.price) if current else None
    return TargetProgressOut(
        instrument_id=inst.id,
        instrument_name=inst.name,
        last_price=market,
        price_year=latest.year if latest else None,
        price_month=latest.month if latest else None,
        target=target_price,
        target_year=current.year if current else None,
        target_month=current.month if current else None,
        progress_pct=progress_pct(market, target_price),
    )
