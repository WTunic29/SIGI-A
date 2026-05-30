from sqlalchemy import Column, BigInteger, Integer, Numeric, String, TIMESTAMP, func
from app.database import Base


class CarritoDetalle(Base):
    __tablename__ = "carrito_detalle"
    __table_args__ = {"schema": "core"}

    id_carrito_detalle = Column(BigInteger, primary_key=True, index=True)

    id_carrito = Column(BigInteger, nullable=False)

    tipo_item = Column(String(20), nullable=False)

    id_producto = Column(BigInteger, nullable=True)
    id_servicio = Column(BigInteger, nullable=True)

    cantidad = Column(Integer, nullable=False, default=1)

    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=True)

    estado_reserva = Column(String(20), nullable=True, default="RESERVADO")

    fecha_reserva = Column(TIMESTAMP, nullable=True, server_default=func.now())
    fecha_expiracion_reserva = Column(TIMESTAMP, nullable=True)

