from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


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
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    ciudad: Optional[str] = None
    categoria_principal: Optional[str] = None
    estado: Optional[str] = None

    class Config:
        from_attributes = True


class CambiarEstadoNegocio(BaseModel):
    nuevo_estado: str

    @field_validator("nuevo_estado")
    @classmethod
    def validar_estado(cls, estado: str):
        estados_permitidos = ["activo", "inactivo", "suspendido"]

        if estado not in estados_permitidos:
            raise ValueError(
                "Estado inválido. Los estados permitidos son: activo, inactivo, suspendido"
            )

        return estado
