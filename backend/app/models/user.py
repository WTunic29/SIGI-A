from sqlalchemy import Column, BigInteger, String, TIMESTAMP
from app.database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "core"}

    id_usuario = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(30))
    password_hash = Column(String(255), nullable=False)
    estado = Column(String(20), default="activo")
    fecha_creacion = Column(TIMESTAMP, default=datetime.utcnow)
    rol = Column(String(20), nullable=False, default="cliente")