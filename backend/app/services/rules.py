from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Broker, Instrument, MonthlyPrice, PriceTarget, Trade
from app.services.balances import instrument_balance, pair_balance


class BusinessRule(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def get_broker(db: Session, broker_id: int) -> Broker:
    row = db.get(Broker, broker_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "broker_not_found")
    return row


def get_instrument(db: Session, instrument_id: int) -> Instrument:
    row = db.get(Instrument, instrument_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "instrument_not_found")
    return row


def get_trade(db: Session, trade_id: int) -> Trade:
    row = db.get(Trade, trade_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "trade_not_found")
    return row


def validate_inactivate(db: Session, instrument: Instrument, active: bool) -> None:
    if active is False and instrument.active is True:
        if instrument_balance(db, instrument.id) > 0:
            raise BusinessRule("cannot_inactivate")


def validate_currency_change(db: Session, instrument: Instrument, currency: str) -> None:
    if currency == instrument.currency:
        return
    has_data = (
        db.scalar(select(Trade.id).where(Trade.instrument_id == instrument.id).limit(1)) is not None
        or db.scalar(select(MonthlyPrice.id).where(MonthlyPrice.instrument_id == instrument.id).limit(1))
        is not None
        or db.scalar(select(PriceTarget.id).where(PriceTarget.instrument_id == instrument.id).limit(1))
        is not None
    )
    if has_data:
        raise BusinessRule("cannot_change_currency")


def validate_trade(
    db: Session,
    *,
    instrument_id: int,
    broker_id: int,
    type: str,
    quantity: Decimal,
    exclude_id: int | None = None,
) -> None:
    get_broker(db, broker_id)
    inst = get_instrument(db, instrument_id)
    if type == "buy" and not inst.active:
        raise BusinessRule("cannot_buy_inactive")
    actual = pair_balance(db, instrument_id, broker_id, exclude_id=exclude_id)
    if type == "sell" and quantity > actual:
        raise BusinessRule("sell_exceeds_balance")
