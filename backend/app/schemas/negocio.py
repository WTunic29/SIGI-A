from typing import Optional
from pydantic import BaseModel, EmailStr


# =========================
# CREATE
# =========================

class NegocioCreate(BaseModel):
    id_usuario_propietario: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None


# =========================
# UPDATE
# =========================

class NegocioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None


# =========================
# RESPONSE
# =========================

class NegocioResponse(BaseModel):
    id_negocio: int
    id_usuario_propietario: int
    nombre_negocio: str
    descripcion: Optional[str]
    direccion: Optional[str]
    telefono: Optional[str]
    email_negocio: Optional[EmailStr]

    class Config:
        from_attributes = True