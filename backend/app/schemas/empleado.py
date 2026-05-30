from pydantic import BaseModel, EmailStr
from typing import Optional


class EmpleadoCreate(BaseModel):
    id_negocio: int
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = None
    foto_url: Optional[str] = None


class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = None
    foto_url: Optional[str] = None
    estado: Optional[str] = None


class EmpleadoResponse(BaseModel):
    id_empleado: int
    id_negocio: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    email: Optional[EmailStr]
    especialidad: Optional[str]
    foto_url: Optional[str]
    estado: str

    class Config:
        from_attributes = True