from sqlalchemy import Column, BigInteger, Date, Time, String, Text, DateTime
from datetime import datetime
from app.database import Base


class Cita(Base):
    __tablename__ = "citas"

    id_cita = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(BigInteger, nullable=False)
    id_negocio = Column(BigInteger, nullable=False)
    id_empleado = Column(BigInteger, nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)