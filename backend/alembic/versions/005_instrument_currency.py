"""instrument quote currency (COP | USD)

Revision ID: 005_instrument_currency
Revises: 004_fx_rate
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_instrument_currency"
down_revision: str | None = "004_fx_rate"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "instrument",
        sa.Column("currency", sa.String(3), nullable=False, server_default="COP"),
    )
    op.create_check_constraint(
        "ck_instrument_currency",
        "instrument",
        "currency IN ('COP', 'USD')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_instrument_currency", "instrument", type_="check")
    op.drop_column("instrument", "currency")
