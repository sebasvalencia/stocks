from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Instrument, MonthlyPrice
from app.schemas import MissingPriceOut, PendingPricesOut, PriceIn, PriceOut

router = APIRouter(prefix="/prices", tags=["prices"])


def _out(row: MonthlyPrice) -> PriceOut:
    return PriceOut(
        id=row.id,
        instrument_id=row.instrument_id,
        year=row.year,
        month=row.month,
        price=row.price,
        instrument_name=row.instrument.name if row.instrument else None,
        instrument_currency=row.instrument.currency if row.instrument else None,
    )


@router.get("/pending", response_model=PendingPricesOut)
def pending(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> PendingPricesOut:
    active = list(
        db.scalars(select(Instrument).where(Instrument.active.is_(True)).order_by(Instrument.name)).all()
    )
    with_price = {
        row.instrument_id
        for row in db.scalars(
            select(MonthlyPrice).where(MonthlyPrice.year == year, MonthlyPrice.month == month)
        ).all()
    }
    missing = [
        MissingPriceOut(instrument_id=i.id, instrument_name=i.name)
        for i in active
        if i.id not in with_price
    ]
    return PendingPricesOut(
        year=year,
        month=month,
        total_active=len(active),
        pending=len(missing),
        missing=missing,
    )


@router.get("", response_model=list[PriceOut])
def list_prices(
    year: int | None = Query(default=None),
    instrument_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PriceOut]:
    q = select(MonthlyPrice).options(joinedload(MonthlyPrice.instrument))
    if year is not None:
        q = q.where(MonthlyPrice.year == year)
    if instrument_id is not None:
        q = q.where(MonthlyPrice.instrument_id == instrument_id)
    rows = db.scalars(q.order_by(MonthlyPrice.year, MonthlyPrice.month)).all()
    return [_out(r) for r in rows]


@router.put("", response_model=PriceOut)
def upsert(body: PriceIn, db: Session = Depends(get_db)) -> PriceOut:
    inst = db.get(Instrument, body.instrument_id)
    if inst is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    row = db.scalar(
        select(MonthlyPrice).where(
            MonthlyPrice.instrument_id == body.instrument_id,
            MonthlyPrice.year == body.year,
            MonthlyPrice.month == body.month,
        )
    )
    if row is None:
        row = MonthlyPrice(
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
        select(MonthlyPrice)
        .options(joinedload(MonthlyPrice.instrument))
        .where(MonthlyPrice.id == row.id)
    )
    assert row is not None
    return _out(row)


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(price_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(MonthlyPrice, price_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "price_not_found")
    db.delete(row)
    db.commit()
