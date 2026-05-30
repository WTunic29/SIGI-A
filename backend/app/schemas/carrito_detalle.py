from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from datetime import date, time


class CarritoDetalleBase(BaseModel):
    id_carrito: int
    tipo_item: str
    id_negocio: Optional[int] = None
    id_producto: Optional[int] = None
    id_servicio: Optional[int] = None
    id_empleado: Optional[int] = None
    fecha_cita: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    observaciones: Optional[str] = None
    cantidad: int
    precio_unitario: Decimal

    @field_validator("tipo_item")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        tipos = {"producto", "servicio"}
        if value not in tipos:
            raise ValueError("tipo_item debe ser 'producto' o 'servicio'")
        return value


class CarritoDetalleCreate(CarritoDetalleBase):
    pass


class CarritoDetalleUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[Decimal] = None
    observaciones: Optional[str] = None


class CarritoDetalleResponse(CarritoDetalleBase):
    id_carrito_detalle: int
    nombre_item: Optional[str] = None
    nombre_negocio: Optional[str] = None
    nombre_empleado: Optional[str] = None

    class Config:
        from_attributes = True
