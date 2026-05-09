from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ProductoCreate(BaseModel):
    id_negocio: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    stock: int
    imagen_url: Optional[str] = None


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    stock: Optional[int] = None
    imagen_url: Optional[str] = None
    estado: Optional[str] = None


class ProductoResponse(BaseModel):
    id_producto: int
    id_negocio: int
    nombre: str
    descripcion: Optional[str]
    precio: Decimal
    stock: int
    imagen_url: Optional[str]
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True