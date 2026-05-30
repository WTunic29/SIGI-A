from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class TokenActivacion(Base):
    __tablename__ = "tokens_activacion"
    __table_args__ = {"schema": "core"}

    id_token = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("core.usuarios.id_usuario"), nullable=False)

    token = Column(String(255), nullable=False, unique=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)

    usado = Column(Boolean, default=False)