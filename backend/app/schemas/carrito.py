from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CarritoBase(BaseModel):
    id_usuario: int
    estado: str


class CarritoCreate(CarritoBase):
    id_negocio: Optional[int] = None


class CarritoUpdate(BaseModel):
    estado: Optional[str] = None
    id_negocio: Optional[int] = None
    fecha_expiracion: Optional[datetime] = None
    total_estimado: Optional[Decimal] = None


class CarritoResponse(BaseModel):
    id_carrito: int
    id_usuario: int
    id_negocio: Optional[int] = None
    estado: str
    fecha_creacion: Optional[datetime] = None
    fecha_expiracion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    total_estimado: Optional[Decimal] = None

    class Config:
        from_attributes = True
