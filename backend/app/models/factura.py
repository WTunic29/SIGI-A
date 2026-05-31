from sqlalchemy import Column, BigInteger, String, Numeric, TIMESTAMP, Text, ForeignKey, func
from app.database import Base


class Factura(Base):
    __tablename__ = "facturas"
    __table_args__ = {"schema": "core"}

    id_factura = Column(BigInteger, primary_key=True, index=True)
    numero_factura = Column(String(30), nullable=False, unique=True)

    id_pedido = Column(BigInteger, ForeignKey("core.pedidos.id_pedido", ondelete="CASCADE"), nullable=False, unique=True)
    id_usuario = Column(BigInteger, ForeignKey("core.usuarios.id_usuario"), nullable=False)
    id_negocio = Column(BigInteger, ForeignKey("core.negocios.id_negocio", ondelete="CASCADE"), nullable=False)

    subtotal = Column(Numeric(12, 2), nullable=False)
    impuestos = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False)

    estado = Column(String(20), nullable=False, default="emitida")
    correo_destino = Column(String(150), nullable=True)

    fecha_emision = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_envio_correo = Column(TIMESTAMP, nullable=True)

    nombre_archivo_pdf = Column(String(255), nullable=True)
    ruta_pdf = Column(Text, nullable=True)
