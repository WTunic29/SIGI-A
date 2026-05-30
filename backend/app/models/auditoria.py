from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    TIMESTAMP
)
from datetime import datetime

from app.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = {"schema": "core"}

    id_auditoria = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=True)
    correo_usuario = Column(String(150), nullable=True)
    rol_usuario = Column(String(50), nullable=True)

    accion = Column(String(100), nullable=False)
    modulo = Column(String(100), nullable=True)

    tabla_afectada = Column(String(100), nullable=True)
    id_registro = Column(BigInteger, nullable=True)

    metodo_http = Column(String(10), nullable=True)
    ruta = Column(Text, nullable=True)

    detalle = Column(Text, nullable=True)

    ip = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)

    nivel = Column(String(30), default="INFO")
    resultado = Column(String(30), default="OK")

    fecha = Column(TIMESTAMP, default=datetime.utcnow)