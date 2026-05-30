from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime
from datetime import datetime
from app.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(BigInteger, nullable=False)
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(30), nullable=False)
    leida = Column(Boolean, nullable=False, default=False)
    fecha = Column(DateTime, nullable=False, default=datetime.now)