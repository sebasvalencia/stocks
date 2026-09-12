from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FxRate
from app.schemas import FxRateIn, FxRateOut

router = APIRouter(prefix="/fx-rates", tags=["fx"])


@router.get("", response_model=list[FxRateOut])
def list_rates(
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[FxRate]:
    q = select(FxRate)
    if year is not None:
        q = q.where(FxRate.year == year)
    return list(db.scalars(q.order_by(FxRate.year, FxRate.month)).all())


@router.put("", response_model=FxRateOut)
def upsert(body: FxRateIn, db: Session = Depends(get_db)) -> FxRate:
    row = db.scalar(
        select(FxRate).where(FxRate.year == body.year, FxRate.month == body.month)
    )
    if row is None:
        row = FxRate(year=body.year, month=body.month, cop_per_usd=body.cop_per_usd)
        db.add(row)
    else:
        row.cop_per_usd = body.cop_per_usd
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(rate_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(FxRate, rate_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "fx_rate_not_found")
    db.delete(row)
    db.commit()
