from sqlalchemy import Column, BigInteger, Integer, Numeric, String
from app.database import Base


class CarritoDetalle(Base):
    __tablename__ = "carrito_detalle"
    __table_args__ = {"schema": "core"}

    id_carrito_detalle = Column(BigInteger, primary_key=True, index=True)

    id_carrito = Column(BigInteger, nullable=False)

    tipo_item = Column(String(20), nullable=False)

    id_producto = Column(BigInteger)

    id_servicio = Column(BigInteger)

    cantidad = Column(Integer, nullable=False)

    precio_unitario = Column(Numeric(12, 2), nullable=False)