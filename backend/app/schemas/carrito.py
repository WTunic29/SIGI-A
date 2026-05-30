from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CarritoBase(BaseModel):
    id_usuario: int
    estado: str


class CarritoCreate(CarritoBase):
    pass


class CarritoUpdate(BaseModel):
    estado: Optional[str] = None


class CarritoResponse(CarritoBase):
    id_carrito: int
    fecha_creacion: Optional[datetime]

    class Config:
        from_attributes = True