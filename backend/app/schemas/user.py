from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr, field_validator
import re

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    password: str

    @field_validator("password")
    @classmethod
    def validar_password_segura(cls, password: str):
        if len(password) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")

        if not re.search(r"[A-Za-z]", password):
            raise ValueError("La contraseña debe contener al menos una letra")

        if not re.search(r"\d", password):
            raise ValueError("La contraseña debe contener al menos un número")

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("La contraseña debe contener al menos un símbolo")

        return password


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class Verificar2FA(BaseModel):
    correo: EmailStr
    codigo: str