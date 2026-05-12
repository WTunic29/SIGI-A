from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class CarritoDetalleBase(BaseModel):
    id_carrito: int
    tipo_item: str
    id_producto: Optional[int] = None
    id_servicio: Optional[int] = None
    cantidad: int
    precio_unitario: Decimal


class CarritoDetalleCreate(CarritoDetalleBase):
    pass


class CarritoDetalleUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[Decimal] = None


class CarritoDetalleResponse(CarritoDetalleBase):
    id_carrito_detalle: int

    class Config:
        from_attributes = True