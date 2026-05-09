from sqlalchemy import Column, BigInteger, Numeric, Integer
from app.database import Base


class DetalleCita(Base):
    __tablename__ = "detalle_cita"

    id_detalle_cita = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_cita = Column(BigInteger, nullable=False)
    id_servicio = Column(BigInteger, nullable=False)
    precio = Column(Numeric(12, 2), nullable=False)
    duracion = Column(Integer, nullable=False)