"""tablas 3FN: corredor, instrumento, movimiento, precio_mensual

Revision ID: 001_initial_3fn
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_3fn"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "corredor",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False, unique=True),
    )
    op.create_table(
        "instrumento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False, unique=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "movimiento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instrumento_id", sa.Integer(), sa.ForeignKey("instrumento.id"), nullable=False),
        sa.Column("corredor_id", sa.Integer(), sa.ForeignKey("corredor.id"), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("anio", sa.SmallInteger(), nullable=False),
        sa.Column("mes", sa.SmallInteger(), nullable=True),
        sa.Column("cantidad", sa.Numeric(18, 6), nullable=False),
        sa.CheckConstraint("tipo IN ('compra', 'venta')", name="ck_movimiento_tipo"),
        sa.CheckConstraint("cantidad > 0", name="ck_movimiento_cantidad"),
        sa.CheckConstraint("mes IS NULL OR (mes >= 1 AND mes <= 12)", name="ck_movimiento_mes"),
    )
    op.create_table(
        "precio_mensual",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instrumento_id", sa.Integer(), sa.ForeignKey("instrumento.id"), nullable=False),
        sa.Column("anio", sa.SmallInteger(), nullable=False),
        sa.Column("mes", sa.SmallInteger(), nullable=False),
        sa.Column("precio", sa.Numeric(18, 4), nullable=False),
        sa.UniqueConstraint("instrumento_id", "anio", "mes", name="uq_precio_instrumento_periodo"),
        sa.CheckConstraint("mes >= 1 AND mes <= 12", name="ck_precio_mes"),
        sa.CheckConstraint("precio > 0", name="ck_precio_valor"),
    )


def downgrade() -> None:
    op.drop_table("precio_mensual")
    op.drop_table("movimiento")
    op.drop_table("instrumento")
    op.drop_table("corredor")
