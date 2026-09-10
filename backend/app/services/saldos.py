from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Movimiento


def saldo_par(
    db: Session,
    instrumento_id: int,
    corredor_id: int,
    exclude_id: int | None = None,
) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (Movimiento.tipo == "compra", Movimiento.cantidad),
                else_=-Movimiento.cantidad,
            )
        ),
        0,
    )
    q = select(expr).where(
        Movimiento.instrumento_id == instrumento_id,
        Movimiento.corredor_id == corredor_id,
    )
    if exclude_id is not None:
        q = q.where(Movimiento.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)


def saldo_titulo(db: Session, instrumento_id: int, exclude_id: int | None = None) -> Decimal:
    expr = func.coalesce(
        func.sum(
            case(
                (Movimiento.tipo == "compra", Movimiento.cantidad),
                else_=-Movimiento.cantidad,
            )
        ),
        0,
    )
    q = select(expr).where(Movimiento.instrumento_id == instrumento_id)
    if exclude_id is not None:
        q = q.where(Movimiento.id != exclude_id)
    value = db.execute(q).scalar_one()
    return Decimal(value)
