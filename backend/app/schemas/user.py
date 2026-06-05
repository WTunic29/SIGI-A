from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

import re

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    genero: str
    password: str
    rol: str = "cliente"


    @field_validator("genero")
    @classmethod
    def validar_genero(cls, genero: str):
        genero = genero.strip().lower()

        equivalencias = {
            "masculino": "masculino",
            "femenino": "femenino",
            "otro": "otro",
            "prefiero_no_decir": "prefiero_no_decir",
            "prefiero no decir": "prefiero_no_decir",
            "prefiero no decirlo": "prefiero_no_decir"
        }

        genero_normalizado = equivalencias.get(genero)

        if not genero_normalizado:
            raise ValueError("Género inválido")

        return genero_normalizado

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

class CambiarRolUsuario(BaseModel):
    nuevo_rol: str

    @field_validator("nuevo_rol")
    @classmethod
    def validar_rol(cls, rol: str):
        roles_permitidos = ["cliente", "negocio", "admin", "superadmin"]

        if rol not in roles_permitidos:
            raise ValueError(
                "Rol inválido. Los roles permitidos son: cliente, negocio, admin, superadmin"
            )

        return rol


class CambiarEstadoUsuario(BaseModel):
    nuevo_estado: str

    @field_validator("nuevo_estado")
    @classmethod
    def validar_estado(cls, estado: str):
        estados_permitidos = ["activo", "inactivo", "bloqueado", "pendiente"]

        if estado not in estados_permitidos:
            raise ValueError(
                "Estado inválido. Los estados permitidos son: activo, inactivo, bloqueado, pendiente"
            )

        return estado

class ConfirmarMFA(BaseModel):
    codigo: str

class VerificarMFA(BaseModel):
    correo: EmailStr
    codigo: str

class ForgotPasswordRequest(BaseModel):
    correo: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str

    @field_validator("nueva_password")
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
