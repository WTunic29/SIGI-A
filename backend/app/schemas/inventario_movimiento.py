from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InventarioMovimientoCreate(BaseModel):
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    motivo: Optional[str] = None


class InventarioMovimientoResponse(BaseModel):
    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    motivo: Optional[str]
    fecha: datetime

    class Config:
        from_attributes = True