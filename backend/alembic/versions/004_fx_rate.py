"""monthly TRM (COP per 1 USD)

Revision ID: 004_fx_rate
Revises: 003_english_schema
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_fx_rate"
down_revision: str | None = "003_english_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fx_rate",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("cop_per_usd", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("year", "month", name="uq_fx_rate_period"),
        sa.CheckConstraint("month >= 1 AND month <= 12", name="ck_fx_rate_month"),
        sa.CheckConstraint("cop_per_usd > 0", name="ck_fx_rate_value"),
    )


def downgrade() -> None:
    op.drop_table("fx_rate")
