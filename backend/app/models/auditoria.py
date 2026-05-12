from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    TIMESTAMP
)

from app.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = {"schema": "core"}

    id_auditoria = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    accion = Column(String(100), nullable=False)

    tabla_afectada = Column(String(100), nullable=False)

    id_registro = Column(BigInteger, nullable=False)

    detalle = Column(Text)

    fecha = Column(TIMESTAMP)