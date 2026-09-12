"""rename schema to English; compra/venta → buy/sell

Revision ID: 003_english_schema
Revises: 002_comision_objetivo
"""

from collections.abc import Sequence

from alembic import op

revision: str = "003_english_schema"
down_revision: str | None = "002_comision_objetivo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_movimiento_tipo", "movimiento", type_="check")
    op.drop_constraint("ck_movimiento_cantidad", "movimiento", type_="check")
    op.drop_constraint("ck_movimiento_comision", "movimiento", type_="check")
    op.drop_constraint("ck_movimiento_mes", "movimiento", type_="check")
    op.drop_constraint("ck_precio_mes", "precio_mensual", type_="check")
    op.drop_constraint("ck_precio_valor", "precio_mensual", type_="check")
    op.drop_constraint("ck_objetivo_mes", "objetivo_precio", type_="check")
    op.drop_constraint("ck_objetivo_valor", "objetivo_precio", type_="check")
    op.drop_constraint("uq_precio_instrumento_periodo", "precio_mensual", type_="unique")
    op.drop_constraint("uq_objetivo_instrumento_periodo", "objetivo_precio", type_="unique")

    op.rename_table("corredor", "broker")
    op.rename_table("instrumento", "instrument")
    op.rename_table("movimiento", "trade")
    op.rename_table("precio_mensual", "monthly_price")
    op.rename_table("objetivo_precio", "price_target")

    op.alter_column("broker", "nombre", new_column_name="name")
    op.alter_column("instrument", "nombre", new_column_name="name")
    op.alter_column("instrument", "activo", new_column_name="active")

    op.alter_column("trade", "instrumento_id", new_column_name="instrument_id")
    op.alter_column("trade", "corredor_id", new_column_name="broker_id")
    op.alter_column("trade", "tipo", new_column_name="type")
    op.alter_column("trade", "anio", new_column_name="year")
    op.alter_column("trade", "mes", new_column_name="month")
    op.alter_column("trade", "cantidad", new_column_name="quantity")
    op.alter_column("trade", "comision", new_column_name="commission")

    op.alter_column("monthly_price", "instrumento_id", new_column_name="instrument_id")
    op.alter_column("monthly_price", "anio", new_column_name="year")
    op.alter_column("monthly_price", "mes", new_column_name="month")
    op.alter_column("monthly_price", "precio", new_column_name="price")

    op.alter_column("price_target", "instrumento_id", new_column_name="instrument_id")
    op.alter_column("price_target", "anio", new_column_name="year")
    op.alter_column("price_target", "mes", new_column_name="month")
    op.alter_column("price_target", "precio", new_column_name="price")

    op.execute("UPDATE trade SET type = 'buy' WHERE type = 'compra'")
    op.execute("UPDATE trade SET type = 'sell' WHERE type = 'venta'")

    op.create_check_constraint("ck_trade_type", "trade", "type IN ('buy', 'sell')")
    op.create_check_constraint("ck_trade_quantity", "trade", "quantity > 0")
    op.create_check_constraint("ck_trade_commission", "trade", "commission >= 0")
    op.create_check_constraint(
        "ck_trade_month", "trade", "month IS NULL OR (month >= 1 AND month <= 12)"
    )
    op.create_check_constraint("ck_monthly_price_month", "monthly_price", "month >= 1 AND month <= 12")
    op.create_check_constraint("ck_monthly_price_value", "monthly_price", "price > 0")
    op.create_check_constraint("ck_price_target_month", "price_target", "month >= 1 AND month <= 12")
    op.create_check_constraint("ck_price_target_value", "price_target", "price > 0")
    op.create_unique_constraint(
        "uq_monthly_price_instrument_period",
        "monthly_price",
        ["instrument_id", "year", "month"],
    )
    op.create_unique_constraint(
        "uq_price_target_instrument_period",
        "price_target",
        ["instrument_id", "year", "month"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_price_target_instrument_period", "price_target", type_="unique")
    op.drop_constraint("uq_monthly_price_instrument_period", "monthly_price", type_="unique")
    op.drop_constraint("ck_price_target_value", "price_target", type_="check")
    op.drop_constraint("ck_price_target_month", "price_target", type_="check")
    op.drop_constraint("ck_monthly_price_value", "monthly_price", type_="check")
    op.drop_constraint("ck_monthly_price_month", "monthly_price", type_="check")
    op.drop_constraint("ck_trade_month", "trade", type_="check")
    op.drop_constraint("ck_trade_commission", "trade", type_="check")
    op.drop_constraint("ck_trade_quantity", "trade", type_="check")
    op.drop_constraint("ck_trade_type", "trade", type_="check")

    op.execute("UPDATE trade SET type = 'compra' WHERE type = 'buy'")
    op.execute("UPDATE trade SET type = 'venta' WHERE type = 'sell'")

    op.alter_column("price_target", "price", new_column_name="precio")
    op.alter_column("price_target", "month", new_column_name="mes")
    op.alter_column("price_target", "year", new_column_name="anio")
    op.alter_column("price_target", "instrument_id", new_column_name="instrumento_id")
    op.alter_column("monthly_price", "price", new_column_name="precio")
    op.alter_column("monthly_price", "month", new_column_name="mes")
    op.alter_column("monthly_price", "year", new_column_name="anio")
    op.alter_column("monthly_price", "instrument_id", new_column_name="instrumento_id")
    op.alter_column("trade", "commission", new_column_name="comision")
    op.alter_column("trade", "quantity", new_column_name="cantidad")
    op.alter_column("trade", "month", new_column_name="mes")
    op.alter_column("trade", "year", new_column_name="anio")
    op.alter_column("trade", "type", new_column_name="tipo")
    op.alter_column("trade", "broker_id", new_column_name="corredor_id")
    op.alter_column("trade", "instrument_id", new_column_name="instrumento_id")
    op.alter_column("instrument", "active", new_column_name="activo")
    op.alter_column("instrument", "name", new_column_name="nombre")
    op.alter_column("broker", "name", new_column_name="nombre")

    op.rename_table("price_target", "objetivo_precio")
    op.rename_table("monthly_price", "precio_mensual")
    op.rename_table("trade", "movimiento")
    op.rename_table("instrument", "instrumento")
    op.rename_table("broker", "corredor")

    op.create_unique_constraint(
        "uq_objetivo_instrumento_periodo",
        "objetivo_precio",
        ["instrumento_id", "anio", "mes"],
    )
    op.create_unique_constraint(
        "uq_precio_instrumento_periodo",
        "precio_mensual",
        ["instrumento_id", "anio", "mes"],
    )
    op.create_check_constraint("ck_objetivo_valor", "objetivo_precio", "precio > 0")
    op.create_check_constraint("ck_objetivo_mes", "objetivo_precio", "mes >= 1 AND mes <= 12")
    op.create_check_constraint("ck_precio_valor", "precio_mensual", "precio > 0")
    op.create_check_constraint("ck_precio_mes", "precio_mensual", "mes >= 1 AND mes <= 12")
    op.create_check_constraint("ck_movimiento_mes", "movimiento", "mes IS NULL OR (mes >= 1 AND mes <= 12)")
    op.create_check_constraint("ck_movimiento_comision", "movimiento", "comision >= 0")
    op.create_check_constraint("ck_movimiento_cantidad", "movimiento", "cantidad > 0")
    op.create_check_constraint("ck_movimiento_tipo", "movimiento", "tipo IN ('compra', 'venta')")
