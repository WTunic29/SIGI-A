from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PedidoDetalleBase(BaseModel):
    id_pedido: int
    tipo_item: str
    id_producto: Optional[int] = None
    id_servicio: Optional[int] = None
    id_cita: Optional[int] = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class PedidoDetalleCreate(PedidoDetalleBase):
    pass


class PedidoDetalleUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None


class PedidoDetalleResponse(PedidoDetalleBase):
    id_pedido_detalle: int

    class Config:
        from_attributes = True