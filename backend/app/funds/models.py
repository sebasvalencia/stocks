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


class Fiduciary(Base):
    __tablename__ = "fiduciary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    trades: Mapped[list["FundTrade"]] = relationship(back_populates="fiduciary")


class Fund(Base):
    __tablename__ = "fund"
    __table_args__ = (CheckConstraint("currency IN ('COP', 'USD')", name="ck_fund_currency"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="COP", server_default="COP")

    trades: Mapped[list["FundTrade"]] = relationship(back_populates="fund")
    unit_values: Mapped[list["FundUnitValue"]] = relationship(back_populates="fund")
    targets: Mapped[list["FundTarget"]] = relationship(back_populates="fund")


class FundTrade(Base):
    __tablename__ = "fund_trade"
    __table_args__ = (
        CheckConstraint("type IN ('subscribe', 'redeem')", name="ck_fund_trade_type"),
        CheckConstraint("quantity > 0", name="ck_fund_trade_quantity"),
        CheckConstraint("commission >= 0", name="ck_fund_trade_commission"),
        CheckConstraint("price IS NULL OR price > 0", name="ck_fund_trade_price"),
        CheckConstraint("month IS NULL OR (month >= 1 AND month <= 12)", name="ck_fund_trade_month"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("fund.id"), nullable=False)
    fiduciary_id: Mapped[int] = mapped_column(ForeignKey("fiduciary.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    commission: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0"))
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    fund: Mapped[Fund] = relationship(back_populates="trades")
    fiduciary: Mapped[Fiduciary] = relationship(back_populates="trades")


class FundUnitValue(Base):
    __tablename__ = "fund_unit_value"
    __table_args__ = (
        UniqueConstraint("fund_id", "year", "month", name="uq_fund_unit_value_period"),
        CheckConstraint("month >= 1 AND month <= 12", name="ck_fund_unit_value_month"),
        CheckConstraint("value > 0", name="ck_fund_unit_value_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("fund.id"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    fund: Mapped[Fund] = relationship(back_populates="unit_values")


class FundTarget(Base):
    __tablename__ = "fund_target"
    __table_args__ = (
        UniqueConstraint("fund_id", "year", "month", name="uq_fund_target_period"),
        CheckConstraint("month >= 1 AND month <= 12", name="ck_fund_target_month"),
        CheckConstraint("price > 0", name="ck_fund_target_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("fund.id"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    fund: Mapped[Fund] = relationship(back_populates="targets")
