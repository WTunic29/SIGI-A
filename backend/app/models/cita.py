from sqlalchemy import Column, BigInteger, String, Date, Time, TIMESTAMP, Text, func
from app.database import Base


class Cita(Base):
    __tablename__ = "citas"
    __table_args__ = {"schema": "core"}

    id_cita = Column(BigInteger, primary_key=True, index=True)

    id_cliente = Column(BigInteger, nullable=False)
    id_negocio = Column(BigInteger, nullable=False)
    id_empleado = Column(BigInteger, nullable=False)

    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    estado = Column(String(30), nullable=False, default="pendiente")
    observaciones = Column(Text)

    fecha_creacion = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )