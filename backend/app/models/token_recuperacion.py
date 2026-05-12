from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Boolean
from app.database import Base


class TokenRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"
    __table_args__ = {"schema": "core"}

    id_token = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    token = Column(String(255), nullable=False)

    fecha_creacion = Column(TIMESTAMP)

    fecha_expiracion = Column(TIMESTAMP)

    usado = Column(Boolean, default=False)