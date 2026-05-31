from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PagoBase(BaseModel):
    id_pedido: int
    metodo_pago: str
    referencia_externa: Optional[str] = None
    estado_pago: Optional[str] = "pendiente"
    valor: Decimal
    respuesta_pasarela: Optional[str] = None
    correo_factura: Optional[EmailStr] = None


class PagoCreate(PagoBase):
    pass


class PagoUpdate(BaseModel):
    metodo_pago: Optional[str] = None
    referencia_externa: Optional[str] = None
    estado_pago: Optional[str] = None
    valor: Optional[Decimal] = None
    respuesta_pasarela: Optional[str] = None


class PagoResponse(PagoBase):
    id_pago: int
    fecha_pago: Optional[datetime]

    class Config:
        from_attributes = True
