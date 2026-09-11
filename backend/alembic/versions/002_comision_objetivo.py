"""comision en movimiento y tabla objetivo_precio

Revision ID: 002_comision_objetivo
Revises: 001_initial_3fn
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_comision_objetivo"
down_revision: str | None = "001_initial_3fn"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "movimiento",
        sa.Column(
            "comision",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint("ck_movimiento_comision", "movimiento", "comision >= 0")
    op.create_table(
        "objetivo_precio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instrumento_id", sa.Integer(), sa.ForeignKey("instrumento.id"), nullable=False),
        sa.Column("anio", sa.SmallInteger(), nullable=False),
        sa.Column("mes", sa.SmallInteger(), nullable=False),
        sa.Column("precio", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("instrumento_id", "anio", "mes", name="uq_objetivo_instrumento_periodo"),
        sa.CheckConstraint("mes >= 1 AND mes <= 12", name="ck_objetivo_mes"),
        sa.CheckConstraint("precio > 0", name="ck_objetivo_valor"),
    )
    op.alter_column("movimiento", "comision", server_default=None)


def downgrade() -> None:
    op.drop_table("objetivo_precio")
    op.drop_constraint("ck_movimiento_comision", "movimiento", type_="check")
    op.drop_column("movimiento", "comision")
