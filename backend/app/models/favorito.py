from sqlalchemy import Column, BigInteger, TIMESTAMP
from app.database import Base


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = {"schema": "core"}

    id_favorito = Column(BigInteger, primary_key=True, index=True)

    id_usuario = Column(BigInteger, nullable=False)

    id_negocio = Column(BigInteger, nullable=False)

    fecha = Column(TIMESTAMP)