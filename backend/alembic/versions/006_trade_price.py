"""trade unit price (nullable, > 0)

Revision ID: 006_trade_price
Revises: 005_instrument_currency
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_trade_price"
down_revision: str | None = "005_instrument_currency"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("trade", sa.Column("price", sa.Numeric(18, 4), nullable=True))
    op.create_check_constraint(
        "ck_trade_price",
        "trade",
        "price IS NULL OR price > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_trade_price", "trade", type_="check")
    op.drop_column("trade", "price")
