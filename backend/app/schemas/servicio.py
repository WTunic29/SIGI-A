from typing import Optional
from pydantic import BaseModel


# =========================
# CREATE
# =========================

class ServicioCreate(BaseModel):
    id_negocio: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    duracion_minutos: int
    precio: float
    imagen_url: Optional[str] = None


# =========================
# UPDATE
# =========================

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_minutos: Optional[int] = None
    precio: Optional[float] = None
    estado: Optional[str] = None
    imagen_url: Optional[str] = None


# =========================
# RESPONSE
# =========================

class ServicioResponse(BaseModel):
    id_servicio: int
    id_negocio: int
    nombre: str
    descripcion: Optional[str]
    duracion_minutos: int
    precio: float
    estado: str
    imagen_url: Optional[str]

    class Config:
        from_attributes = True