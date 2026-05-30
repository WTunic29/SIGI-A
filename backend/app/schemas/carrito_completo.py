from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.carrito import CarritoResponse
from app.schemas.carrito_detalle import CarritoDetalleResponse


class CarritoActivoResponse(BaseModel):
    carrito: CarritoResponse
    detalles: List[CarritoDetalleResponse]
    total: float
    cantidad_items: int
