from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class CarritoDetalleBase(BaseModel):
    id_carrito: int
    tipo_item: str
    id_producto: Optional[int] = None
    id_servicio: Optional[int] = None
    id_cita: Optional[int] = None
    cantidad: int
    precio_unitario: Decimal


class CarritoDetalleCreate(CarritoDetalleBase):
    pass


class CarritoDetalleUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[Decimal] = None


class CarritoDetalleResponse(CarritoDetalleBase):
    id_carrito_detalle: int
    subtotal: Optional[Decimal] = None
    estado_reserva: Optional[str] = None
    fecha_reserva: Optional[datetime] = None
    fecha_expiracion_reserva: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgregarProductoCarrito(BaseModel):
    id_producto: int
    cantidad: int = 1

class AgregarCitaCarrito(BaseModel):
    id_negocio: int
    id_empleado: int
    id_servicio: int
    fecha: str
    hora_inicio: str
    observaciones: Optional[str] = None
