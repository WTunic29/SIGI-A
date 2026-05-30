from sqlalchemy import Column, BigInteger, String, Numeric, TIMESTAMP, func
from app.database import Base


class Factura(Base):
    __tablename__ = "facturas"
    __table_args__ = {"schema": "core"}

    id_factura = Column(BigInteger, primary_key=True, index=True)
    id_pedido = Column(BigInteger, nullable=False)
    id_pago = Column(BigInteger, nullable=False)
    numero_factura = Column(String(30), nullable=False, unique=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), nullable=False, default="emitida")
    fecha_emision = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )
