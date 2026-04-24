from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    password: str


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str