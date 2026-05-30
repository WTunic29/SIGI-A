from sqlalchemy import Column, BigInteger, String, Text, Integer, Numeric, ForeignKey
from app.database import Base


class Servicio(Base):
    __tablename__ = "servicios"
    __table_args__ = {"schema": "core"}

    id_servicio = Column(BigInteger, primary_key=True, index=True)
    id_negocio = Column(BigInteger, ForeignKey("core.negocios.id_negocio"), nullable=False)

    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=True)
    duracion_minutos = Column(Integer, nullable=False)
    precio = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), default="activo")
    imagen_url = Column(Text, nullable=True)