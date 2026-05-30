from sqlalchemy import Column, BigInteger, String, Numeric, Text, TIMESTAMP
from app.database import Base


class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = {"schema": "core"}

    id_pago = Column(BigInteger, primary_key=True, index=True)
    id_pedido = Column(BigInteger, nullable=False)

    metodo_pago = Column(String, nullable=False)

    referencia_externa = Column(String)

    estado_pago = Column(
        String,
        nullable=False,
        default="pendiente"
    )

    valor = Column(Numeric, nullable=False)

    fecha_pago = Column(TIMESTAMP)

    respuesta_pasarela = Column(Text)