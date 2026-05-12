from sqlalchemy import Column, BigInteger, SmallInteger, Text, DateTime
from datetime import datetime
from app.database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id_calificacion = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(BigInteger, nullable=False)
    id_negocio = Column(BigInteger, nullable=False)
    id_cita = Column(BigInteger, nullable=False)
    puntuacion = Column(SmallInteger, nullable=False)
    comentario = Column(Text, nullable=True)
    fecha = Column(DateTime, nullable=False, default=datetime.now)