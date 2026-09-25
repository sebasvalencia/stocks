from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas import VisibleDecimal


class FiduciaryIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class FiduciaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FundIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    active: bool = True
    currency: Literal["COP", "USD"] = "COP"


class FundUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    active: bool | None = None
    currency: Literal["COP", "USD"] | None = None


class FundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    active: bool
    currency: str


class FundTradeIn(BaseModel):
    fund_id: int
    fiduciary_id: int
    type: Literal["subscribe", "redeem"]
    year: int = Field(ge=1900, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    quantity: Decimal = Field(gt=0)
    commission: Decimal = Field(default=Decimal("0"), ge=0)
    price: Decimal | None = Field(default=None, gt=0)


class FundTradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    fiduciary_id: int
    type: str
    year: int
    month: int | None
    quantity: VisibleDecimal
    commission: VisibleDecimal
    price: VisibleDecimal | None = None
    fund_name: str | None = None
    fiduciary_name: str | None = None
    fund_currency: str | None = None


class UnitValueIn(BaseModel):
    fund_id: int
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    value: Decimal = Field(gt=0)


class UnitValueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    year: int
    month: int
    value: VisibleDecimal
    fund_name: str | None = None
    fund_currency: str | None = None


class MissingUnitValueOut(BaseModel):
    fund_id: int
    fund_name: str


class PendingUnitValuesOut(BaseModel):
    year: int
    month: int
    total_active: int
    pending: int
    missing: list[MissingUnitValueOut]


class FundTargetIn(BaseModel):
    fund_id: int
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    price: Decimal = Field(gt=0)


class FundTargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_id: int
    year: int
    month: int
    price: VisibleDecimal
    fund_name: str | None = None
    fund_currency: str | None = None


class FundTargetProgressOut(BaseModel):
    fund_id: int
    fund_name: str
    last_price: VisibleDecimal | None
    price_year: int | None
    price_month: int | None
    target: VisibleDecimal | None
    target_year: int | None
    target_month: int | None
    progress_pct: VisibleDecimal | None
    fund_currency: str


class FundVariationPointOut(BaseModel):
    year: int
    month: int
    price: VisibleDecimal
    variation_pct: VisibleDecimal | None


class FundVariationOut(BaseModel):
    fund_id: int
    fund_name: str
    fund_currency: str
    points: list[FundVariationPointOut]
