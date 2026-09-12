from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Trade


def pair_balance(
    db: Session,
    instrument_id: int,
    broker_id: int,
    exclude_id: int | None = None,
) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (Trade.type == "buy", Trade.quantity),
                else_=-Trade.quantity,
            )
        ),
        0,
    )
    q = select(expr).where(
        Trade.instrument_id == instrument_id,
        Trade.broker_id == broker_id,
    )
    if exclude_id is not None:
        q = q.where(Trade.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)


def instrument_balance(db: Session, instrument_id: int, exclude_id: int | None = None) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (Trade.type == "buy", Trade.quantity),
                else_=-Trade.quantity,
            )
        ),
        0,
    )
    q = select(expr).where(Trade.instrument_id == instrument_id)
    if exclude_id is not None:
        q = q.where(Trade.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)
