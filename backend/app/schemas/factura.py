from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class FacturaLineaResponse(BaseModel):
    tipo_item: str
    descripcion: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    id_cita: Optional[int] = None
    fecha_cita: Optional[str] = None
    hora_inicio: Optional[str] = None


class FacturaResponse(BaseModel):
    id_factura: int
    id_pedido: int
    id_pago: int
    numero_factura: str
    subtotal: Decimal
    total: Decimal
    estado: str
    fecha_emision: Optional[datetime] = None
    id_negocio: Optional[int] = None
    nombre_negocio: Optional[str] = None
    metodo_pago: Optional[str] = None
    referencia_externa: Optional[str] = None
    lineas: List[FacturaLineaResponse] = []

    class Config:
        from_attributes = True
