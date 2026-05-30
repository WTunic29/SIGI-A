"""carrito checkout y facturas

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "carrito_detalle",
        sa.Column("id_negocio", sa.BigInteger(), nullable=True),
        schema="core",
    )
    op.add_column(
        "carrito_detalle",
        sa.Column("id_empleado", sa.BigInteger(), nullable=True),
        schema="core",
    )
    op.add_column(
        "carrito_detalle",
        sa.Column("fecha_cita", sa.Date(), nullable=True),
        schema="core",
    )
    op.add_column(
        "carrito_detalle",
        sa.Column("hora_inicio", sa.Time(), nullable=True),
        schema="core",
    )
    op.add_column(
        "carrito_detalle",
        sa.Column("hora_fin", sa.Time(), nullable=True),
        schema="core",
    )
    op.add_column(
        "carrito_detalle",
        sa.Column("observaciones", sa.Text(), nullable=True),
        schema="core",
    )

    op.add_column(
        "pedido_detalle",
        sa.Column("id_cita", sa.BigInteger(), nullable=True),
        schema="core",
    )

    op.create_table(
        "facturas",
        sa.Column("id_factura", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_pedido", sa.BigInteger(), nullable=False),
        sa.Column("id_pago", sa.BigInteger(), nullable=False),
        sa.Column("numero_factura", sa.String(length=30), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("estado", sa.String(length=20), server_default="emitida", nullable=False),
        sa.Column("fecha_emision", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id_factura"),
        sa.UniqueConstraint("numero_factura"),
        schema="core",
    )


def downgrade() -> None:
    op.drop_table("facturas", schema="core")
    op.drop_column("pedido_detalle", "id_cita", schema="core")
    op.drop_column("carrito_detalle", "observaciones", schema="core")
    op.drop_column("carrito_detalle", "hora_fin", schema="core")
    op.drop_column("carrito_detalle", "hora_inicio", schema="core")
    op.drop_column("carrito_detalle", "fecha_cita", schema="core")
    op.drop_column("carrito_detalle", "id_empleado", schema="core")
    op.drop_column("carrito_detalle", "id_negocio", schema="core")
