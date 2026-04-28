from typing import Optional
from pydantic import BaseModel, EmailStr


class NegocioCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None