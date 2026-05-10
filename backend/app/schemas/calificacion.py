from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CalificacionCreate(BaseModel):
    id_cliente: Optional[int] = None
    id_negocio: int
    id_cita: int
    puntuacion: int
    comentario: Optional[str] = None


class CalificacionUpdate(BaseModel):
    puntuacion: Optional[int] = None
    comentario: Optional[str] = None


class CalificacionResponse(BaseModel):
    id_cliente: Optional[int] = None
    id_cliente: int
    id_negocio: int
    id_cita: int
    puntuacion: int
    comentario: Optional[str]
    fecha: datetime

    class Config:
        from_attributes = True