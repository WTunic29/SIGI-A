from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from app.schemas.factura import FacturaResponse
from app.schemas.pedido import PedidoResponse
from app.schemas.pago import PagoResponse


class CheckoutRequest(BaseModel):
    metodo_pago: str = Field(default="efectivo")
    referencia_externa: Optional[str] = None


class CheckoutResultItem(BaseModel):
    id_pedido: int
    id_negocio: int
    total: Decimal
    id_pago: int
    id_factura: int
    numero_factura: str


class CheckoutResponse(BaseModel):
    message: str
    id_carrito: int
    pedidos: List[PedidoResponse]
    pagos: List[PagoResponse]
    facturas: List[FacturaResponse]
    resumen: List[CheckoutResultItem]
