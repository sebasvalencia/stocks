from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Corredor(Base):
    __tablename__ = "corredor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    movimientos: Mapped[list["Movimiento"]] = relationship(back_populates="corredor")


class Instrumento(Base):
    __tablename__ = "instrumento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    movimientos: Mapped[list["Movimiento"]] = relationship(back_populates="instrumento")
    precios: Mapped[list["PrecioMensual"]] = relationship(back_populates="instrumento")


class Movimiento(Base):
    __tablename__ = "movimiento"
    __table_args__ = (
        CheckConstraint("tipo IN ('compra', 'venta')", name="ck_movimiento_tipo"),
        CheckConstraint("cantidad > 0", name="ck_movimiento_cantidad"),
        CheckConstraint("mes IS NULL OR (mes >= 1 AND mes <= 12)", name="ck_movimiento_mes"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrumento_id: Mapped[int] = mapped_column(ForeignKey("instrumento.id"), nullable=False)
    corredor_id: Mapped[int] = mapped_column(ForeignKey("corredor.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    mes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    instrumento: Mapped[Instrumento] = relationship(back_populates="movimientos")
    corredor: Mapped[Corredor] = relationship(back_populates="movimientos")


class PrecioMensual(Base):
    __tablename__ = "precio_mensual"
    __table_args__ = (
        UniqueConstraint("instrumento_id", "anio", "mes", name="uq_precio_instrumento_periodo"),
        CheckConstraint("mes >= 1 AND mes <= 12", name="ck_precio_mes"),
        CheckConstraint("precio > 0", name="ck_precio_valor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrumento_id: Mapped[int] = mapped_column(ForeignKey("instrumento.id"), nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    mes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    instrumento: Mapped[Instrumento] = relationship(back_populates="precios")
