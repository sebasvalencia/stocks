from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.funds.models import FundTrade


def pair_balance(
    db: Session,
    fund_id: int,
    fiduciary_id: int,
    exclude_id: int | None = None,
) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (FundTrade.type == "subscribe", FundTrade.quantity),
                else_=-FundTrade.quantity,
            )
        ),
        0,
    )
    q = select(expr).where(
        FundTrade.fund_id == fund_id,
        FundTrade.fiduciary_id == fiduciary_id,
    )
    if exclude_id is not None:
        q = q.where(FundTrade.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)


def fund_balance(db: Session, fund_id: int, exclude_id: int | None = None) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (FundTrade.type == "subscribe", FundTrade.quantity),
                else_=-FundTrade.quantity,
            )
        ),
        0,
    )
    q = select(expr).where(FundTrade.fund_id == fund_id)
    if exclude_id is not None:
        q = q.where(FundTrade.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)
