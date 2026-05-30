from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP,
    Boolean,
    Text
)

from app.database import Base


class Sesion(Base):
    __tablename__ = "sesiones"
    __table_args__ = {"schema": "core"}

    id_sesion = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    token = Column(String(500), nullable=False)

    fecha_inicio = Column(TIMESTAMP)

    fecha_expiracion = Column(TIMESTAMP)

    ip = Column(String(50))

    user_agent = Column(Text)

    activa = Column(Boolean, default=True)