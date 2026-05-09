from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificacionCreate(BaseModel):
    id_usuario: int
    titulo: str
    mensaje: str
    tipo: str


class NotificacionUpdate(BaseModel):
    leida: Optional[bool] = None


class NotificacionResponse(BaseModel):
    id_notificacion: int
    id_usuario: int
    titulo: str
    mensaje: str
    tipo: str
    leida: bool
    fecha: datetime

    class Config:
        from_attributes = True