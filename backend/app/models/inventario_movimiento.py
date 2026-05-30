from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"

    id_movimiento = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_producto = Column(BigInteger, nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    fecha = Column(DateTime, nullable=False, default=datetime.now)