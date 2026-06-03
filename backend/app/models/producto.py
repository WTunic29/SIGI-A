from sqlalchemy import Column, BigInteger, String, Text, Numeric, Integer, DateTime
from datetime import datetime
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = {"schema": "core"}

    id_producto = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_negocio = Column(BigInteger, nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(12, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    imagen_url = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)