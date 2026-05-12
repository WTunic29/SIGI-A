from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PedidoBase(BaseModel):
    id_usuario: int
    id_negocio: int
    total: Decimal
    estado: str


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    total: Optional[Decimal] = None
    estado: Optional[str] = None


class PedidoResponse(PedidoBase):
    id_pedido: int
    fecha: Optional[datetime]

    class Config:
        from_attributes = True