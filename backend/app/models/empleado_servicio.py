from sqlalchemy import Column, BigInteger
from app.database import Base


class EmpleadoServicio(Base):
    __tablename__ = "empleado_servicio"

    id_empleado_servicio = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_empleado = Column(BigInteger, nullable=False)
    id_servicio = Column(BigInteger, nullable=False)