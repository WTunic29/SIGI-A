from sqlalchemy import Column, BigInteger, String, Text, Numeric, ForeignKey
from app.database import Base


class Negocio(Base):
    __tablename__ = "negocios"
    __table_args__ = {"schema": "core"}

    id_negocio = Column(BigInteger, primary_key=True, index=True)
    id_usuario_propietario = Column(
        BigInteger,
        ForeignKey("core.usuarios.id_usuario"),
        nullable=False
    )

    nombre_negocio = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    direccion = Column(String(255), nullable=True)
    ciudad = Column(String(100), nullable=True)
    latitud = Column(Numeric(9, 6), nullable=True)
    longitud = Column(Numeric(9, 6), nullable=True)
    telefono = Column(String(30), nullable=True)
    email_negocio = Column(String(150), nullable=True)
    logo_url = Column(Text, nullable=True)
    color_primario = Column(String(20), nullable=True)
    color_secundario = Column(String(20), nullable=True)