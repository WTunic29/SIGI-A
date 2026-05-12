from sqlalchemy import Column, BigInteger, Numeric, String, TIMESTAMP
from app.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"
    __table_args__ = {"schema": "core"}

    id_pedido = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    id_negocio = Column(BigInteger, nullable=False)

    total = Column(Numeric(12, 2), nullable=False)

    estado = Column(String(20), nullable=False)

    fecha = Column(TIMESTAMP)