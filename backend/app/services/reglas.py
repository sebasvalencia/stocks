from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Corredor, Instrumento, Movimiento
from app.services.saldos import saldo_par, saldo_titulo


class ReglaNegocio(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def get_corredor(db: Session, corredor_id: int) -> Corredor:
    row = db.get(Corredor, corredor_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corredor no encontrado")
    return row


def get_instrumento(db: Session, instrumento_id: int) -> Instrumento:
    row = db.get(Instrumento, instrumento_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Título no encontrado")
    return row


def get_movimiento(db: Session, movimiento_id: int) -> Movimiento:
    row = db.get(Movimiento, movimiento_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Movimiento no encontrado")
    return row


def validar_inactivar(db: Session, instrumento: Instrumento, activo: bool) -> None:
    if activo is False and instrumento.activo is True:
        if saldo_titulo(db, instrumento.id) > 0:
            raise ReglaNegocio(
                "No se puede inactivar: el título todavía tiene saldo mayor a 0"
            )


def validar_movimiento(
    db: Session,
    *,
    instrumento_id: int,
    corredor_id: int,
    tipo: str,
    cantidad: Decimal,
    exclude_id: int | None = None,
) -> None:
    get_corredor(db, corredor_id)
    inst = get_instrumento(db, instrumento_id)
    if tipo == "compra" and not inst.activo:
        raise ReglaNegocio("No se puede comprar un título inactivo; actívelo primero")
    actual = saldo_par(db, instrumento_id, corredor_id, exclude_id=exclude_id)
    if tipo == "venta":
        if cantidad > actual:
            raise ReglaNegocio(
                f"La venta supera el saldo ({actual} acciones en este corredor)"
            )
