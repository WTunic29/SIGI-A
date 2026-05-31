"""crear tabla facturas

Revision ID: 34f20ed24dec
Revises: b2c3d4e5f6a7
Create Date: 2026-05-31 17:03:50.429692
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "34f20ed24dec"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "facturas",
        sa.Column("id_factura", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("numero_factura", sa.String(length=30), nullable=False),
        sa.Column("id_pedido", sa.BigInteger(), nullable=False),
        sa.Column("id_usuario", sa.BigInteger(), nullable=False),
        sa.Column("id_negocio", sa.BigInteger(), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("impuestos", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="emitida"),
        sa.Column("correo_destino", sa.String(length=150), nullable=True),
        sa.Column("fecha_emision", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("fecha_envio_correo", sa.TIMESTAMP(), nullable=True),
        sa.Column("nombre_archivo_pdf", sa.String(length=255), nullable=True),
        sa.Column("ruta_pdf", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_pedido"], ["core.pedidos.id_pedido"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_usuario"], ["core.usuarios.id_usuario"]),
        sa.ForeignKeyConstraint(["id_negocio"], ["core.negocios.id_negocio"], ondelete="CASCADE"),
        sa.UniqueConstraint("numero_factura", name="uq_facturas_numero"),
        sa.UniqueConstraint("id_pedido", name="uq_facturas_pedido"),
        sa.CheckConstraint("subtotal >= 0", name="facturas_subtotal_check"),
        sa.CheckConstraint("impuestos >= 0", name="facturas_impuestos_check"),
        sa.CheckConstraint("total >= 0", name="facturas_total_check"),
        sa.CheckConstraint(
            "estado IN ('emitida', 'enviada', 'anulada')",
            name="facturas_estado_check"
        ),
        schema="core"
    )

    op.create_index(
        "idx_facturas_pedido",
        "facturas",
        ["id_pedido"],
        schema="core"
    )

    op.create_index(
        "idx_facturas_usuario",
        "facturas",
        ["id_usuario"],
        schema="core"
    )


def downgrade() -> None:
    op.drop_index("idx_facturas_usuario", table_name="facturas", schema="core")
    op.drop_index("idx_facturas_pedido", table_name="facturas", schema="core")
    op.drop_table("facturas", schema="core")
