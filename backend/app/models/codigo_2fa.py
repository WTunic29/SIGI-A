from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Codigo2FA(Base):
    __tablename__ = "codigos_2fa"
    __table_args__ = {"schema": "core"}

    id_codigo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("core.usuarios.id_usuario"), nullable=False)

    codigo = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)

    usado = Column(Boolean, default=False)
    intentos = Column(Integer, default=0)