from sqlalchemy import Column, BigInteger, String, TIMESTAMP
from app.database import Base


class Carrito(Base):
    __tablename__ = "carritos"
    __table_args__ = {"schema": "core"}

    id_carrito = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    estado = Column(String(20), nullable=False)

    fecha_creacion = Column(TIMESTAMP)