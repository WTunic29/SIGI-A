from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditoriaBase(BaseModel):
    id_usuario: int
    accion: str
    tabla_afectada: str
    id_registro: int
    detalle: Optional[str] = None


class AuditoriaCreate(AuditoriaBase):
    pass


class AuditoriaResponse(AuditoriaBase):
    id_auditoria: int
    fecha: Optional[datetime]

    class Config:
        from_attributes = True