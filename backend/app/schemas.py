from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer


def _decimal_sin_ceros(v: Decimal) -> str:
    texto = format(v, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto


DecimalVisible = Annotated[Decimal, PlainSerializer(_decimal_sin_ceros, return_type=str)]


class CorredorIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)


class CorredorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class InstrumentoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    activo: bool = True


class InstrumentoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    activo: bool | None = None


class InstrumentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    activo: bool


class MovimientoIn(BaseModel):
    instrumento_id: int
    corredor_id: int
    tipo: Literal["compra", "venta"]
    anio: int = Field(ge=1900, le=2100)
    mes: int | None = Field(default=None, ge=1, le=12)
    cantidad: Decimal = Field(gt=0)


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrumento_id: int
    corredor_id: int
    tipo: str
    anio: int
    mes: int | None
    cantidad: DecimalVisible
    instrumento_nombre: str | None = None
    corredor_nombre: str | None = None


class PrecioIn(BaseModel):
    instrumento_id: int
    anio: int = Field(ge=1900, le=2100)
    mes: int = Field(ge=1, le=12)
    precio: Decimal = Field(gt=0)


class PrecioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrumento_id: int
    anio: int
    mes: int
    precio: DecimalVisible
    instrumento_nombre: str | None = None


class SaldoOut(BaseModel):
    instrumento_id: int
    instrumento_nombre: str
    corredor_id: int
    corredor_nombre: str
    activo: bool
    saldo: DecimalVisible


class PosicionOut(BaseModel):
    instrumento_id: int
    instrumento_nombre: str
    corredor_id: int
    corredor_nombre: str
    saldo: DecimalVisible
    precio_ultimo: DecimalVisible | None
    anio_precio: int | None
    mes_precio: int | None
    valor: DecimalVisible | None
    peso_pct: DecimalVisible | None
    sin_precio: bool


class ResumenOut(BaseModel):
    total: DecimalVisible
    posiciones: list[PosicionOut]


class VariacionPuntoOut(BaseModel):
    anio: int
    mes: int
    precio: DecimalVisible
    variacion_pct: DecimalVisible | None


class VariacionOut(BaseModel):
    instrumento_id: int
    instrumento_nombre: str
    puntos: list[VariacionPuntoOut]
