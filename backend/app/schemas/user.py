from typing import Optional
from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    password: str
    rol: Optional[str] = "cliente"


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class Verificar2FA(BaseModel):
    correo: EmailStr
    codigo: str