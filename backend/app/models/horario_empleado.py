from sqlalchemy import Column, BigInteger, SmallInteger, Time, Boolean
from app.database import Base


class HorarioEmpleado(Base):
    __tablename__ = "horarios_empleado"

    id_horario = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_empleado = Column(BigInteger, nullable=False)
    dia_semana = Column(SmallInteger, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    disponible = Column(Boolean, nullable=False, default=True)