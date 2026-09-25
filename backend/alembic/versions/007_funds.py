"""FIC tables: fiduciary, fund, fund_trade, fund_unit_value, fund_target

Revision ID: 007_funds
Revises: 006_trade_price
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_funds"
down_revision: str | None = "006_trade_price"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fiduciary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
    )
    op.create_table(
        "fund",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("currency", sa.String(3), nullable=False, server_default="COP"),
        sa.CheckConstraint("currency IN ('COP', 'USD')", name="ck_fund_currency"),
    )
    op.create_table(
        "fund_trade",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fund_id", sa.Integer(), sa.ForeignKey("fund.id"), nullable=False),
        sa.Column("fiduciary_id", sa.Integer(), sa.ForeignKey("fiduciary.id"), nullable=False),
        sa.Column("type", sa.String(10), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("commission", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("price", sa.Numeric(18, 4), nullable=True),
        sa.CheckConstraint("type IN ('subscribe', 'redeem')", name="ck_fund_trade_type"),
        sa.CheckConstraint("quantity > 0", name="ck_fund_trade_quantity"),
        sa.CheckConstraint("commission >= 0", name="ck_fund_trade_commission"),
        sa.CheckConstraint("price IS NULL OR price > 0", name="ck_fund_trade_price"),
        sa.CheckConstraint("month IS NULL OR (month >= 1 AND month <= 12)", name="ck_fund_trade_month"),
    )
    op.create_table(
        "fund_unit_value",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fund_id", sa.Integer(), sa.ForeignKey("fund.id"), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("fund_id", "year", "month", name="uq_fund_unit_value_period"),
        sa.CheckConstraint("month >= 1 AND month <= 12", name="ck_fund_unit_value_month"),
        sa.CheckConstraint("value > 0", name="ck_fund_unit_value_value"),
    )
    op.create_table(
        "fund_target",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fund_id", sa.Integer(), sa.ForeignKey("fund.id"), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("price", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("fund_id", "year", "month", name="uq_fund_target_period"),
        sa.CheckConstraint("month >= 1 AND month <= 12", name="ck_fund_target_month"),
        sa.CheckConstraint("price > 0", name="ck_fund_target_value"),
    )


def downgrade() -> None:
    op.drop_table("fund_target")
    op.drop_table("fund_unit_value")
    op.drop_table("fund_trade")
    op.drop_table("fund")
    op.drop_table("fiduciary")
