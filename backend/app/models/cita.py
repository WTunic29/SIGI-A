from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP,
    Text
)

from app.database import Base


class Cita(Base):
    __tablename__ = "citas"
    __table_args__ = {"schema": "core"}

    id_cita = Column(BigInteger, primary_key=True, index=True)

    id_cliente = Column(BigInteger, nullable=False)

    id_negocio = Column(BigInteger, nullable=False)

    id_empleado = Column(BigInteger, nullable=False)

    fecha_hora_inicio = Column(TIMESTAMP, nullable=False)

    fecha_hora_fin = Column(TIMESTAMP, nullable=False)

    estado = Column(
        String(30),
        nullable=False,
        default="pendiente"
    )

    observaciones = Column(Text)