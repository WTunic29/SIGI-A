from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditoriaBase(BaseModel):
    id_usuario: Optional[int] = None
    correo_usuario: Optional[str] = None
    rol_usuario: Optional[str] = None

    accion: str
    modulo: Optional[str] = None

    tabla_afectada: Optional[str] = None
    id_registro: Optional[int] = None

    metodo_http: Optional[str] = None
    ruta: Optional[str] = None

    detalle: Optional[str] = None

    ip: Optional[str] = None
    user_agent: Optional[str] = None

    nivel: Optional[str] = "INFO"
    resultado: Optional[str] = "OK"


class AuditoriaCreate(AuditoriaBase):
    pass


class AuditoriaResponse(AuditoriaBase):
    id_auditoria: int
    fecha: Optional[datetime]

    class Config:
        from_attributes = True