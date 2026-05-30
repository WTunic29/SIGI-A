from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SesionBase(BaseModel):
    id_usuario: int
    token: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    activa: Optional[bool] = True


class SesionCreate(SesionBase):
    fecha_expiracion: datetime


class SesionUpdate(BaseModel):
    activa: Optional[bool] = None


class SesionResponse(SesionBase):
    id_sesion: int
    fecha_inicio: Optional[datetime]
    fecha_expiracion: Optional[datetime]

    class Config:
        from_attributes = True