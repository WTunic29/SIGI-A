from sqlalchemy import Column, BigInteger, String, Text
from app.database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id_empleado = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_negocio = Column(BigInteger, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    especialidad = Column(String(120), nullable=True)
    foto_url = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="activo")