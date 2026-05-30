from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Numeric, func
from app.database import Base


class Carrito(Base):
    __tablename__ = "carritos"
    __table_args__ = {"schema": "core"}

    id_carrito = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)
    id_negocio = Column(BigInteger, nullable=True)

    estado = Column(String(20), nullable=False, default="activo")

    fecha_creacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_expiracion = Column(TIMESTAMP, nullable=True)
    fecha_actualizacion = Column(TIMESTAMP, nullable=True, server_default=func.now())

    total_estimado = Column(Numeric(12, 2), nullable=True, default=0)
