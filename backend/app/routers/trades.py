from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Trade
from app.schemas import TradeIn, TradeOut
from app.services.balances import pair_balance
from app.services.rules import get_trade, validate_trade

router = APIRouter(prefix="/trades", tags=["trades"])


def _out(row: Trade) -> TradeOut:
    return TradeOut(
        id=row.id,
        instrument_id=row.instrument_id,
        broker_id=row.broker_id,
        type=row.type,
        year=row.year,
        month=row.month,
        quantity=row.quantity,
        commission=row.commission,
        instrument_name=row.instrument.name if row.instrument else None,
        broker_name=row.broker.name if row.broker else None,
    )


@router.get("", response_model=list[TradeOut])
def list_trades(db: Session = Depends(get_db)) -> list[TradeOut]:
    rows = db.scalars(
        select(Trade)
        .options(joinedload(Trade.instrument), joinedload(Trade.broker))
        .order_by(Trade.year.desc(), Trade.id.desc())
    ).all()
    return [_out(r) for r in rows]


@router.get("/{trade_id}", response_model=TradeOut)
def get_one(trade_id: int, db: Session = Depends(get_db)) -> TradeOut:
    row = get_trade(db, trade_id)
    return _out(row)


@router.post("", response_model=TradeOut, status_code=status.HTTP_201_CREATED)
def create(body: TradeIn, db: Session = Depends(get_db)) -> TradeOut:
    validate_trade(
        db,
        instrument_id=body.instrument_id,
        broker_id=body.broker_id,
        type=body.type,
        quantity=body.quantity,
    )
    row = Trade(
        instrument_id=body.instrument_id,
        broker_id=body.broker_id,
        type=body.type,
        year=body.year,
        month=body.month,
        quantity=body.quantity,
        commission=body.commission,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    row = get_trade(db, row.id)
    return _out(row)


@router.put("/{trade_id}", response_model=TradeOut)
def update(trade_id: int, body: TradeIn, db: Session = Depends(get_db)) -> TradeOut:
    row = get_trade(db, trade_id)
    validate_trade(
        db,
        instrument_id=body.instrument_id,
        broker_id=body.broker_id,
        type=body.type,
        quantity=body.quantity,
        exclude_id=row.id,
    )
    row.instrument_id = body.instrument_id
    row.broker_id = body.broker_id
    row.type = body.type
    row.year = body.year
    row.month = body.month
    row.quantity = body.quantity
    row.commission = body.commission
    db.commit()
    db.refresh(row)
    row = get_trade(db, row.id)
    return _out(row)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(trade_id: int, db: Session = Depends(get_db)) -> None:
    row = get_trade(db, trade_id)
    remaining = pair_balance(db, row.instrument_id, row.broker_id, exclude_id=row.id)
    if remaining < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot_delete_trade")
    db.delete(row)
    db.commit()
