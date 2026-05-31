from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal


class FacturaBase(BaseModel):
    numero_factura: str
    id_pedido: int
    id_usuario: int
    id_negocio: int
    subtotal: Decimal
    impuestos: Decimal = Decimal("0.00")
    total: Decimal
    estado: str = "emitida"
    correo_destino: Optional[EmailStr] = None
    nombre_archivo_pdf: Optional[str] = None
    ruta_pdf: Optional[str] = None


class FacturaCreate(BaseModel):
    id_pedido: int
    correo_destino: Optional[EmailStr] = None


class FacturaResponse(FacturaBase):
    id_factura: int
    fecha_emision: Optional[datetime] = None
    fecha_envio_correo: Optional[datetime] = None

    class Config:
        from_attributes = True
