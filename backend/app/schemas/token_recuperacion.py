from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenRecuperacionBase(BaseModel):
    id_usuario: int
    token: str
    usado: Optional[bool] = False


class TokenRecuperacionCreate(TokenRecuperacionBase):
    fecha_expiracion: datetime


class TokenRecuperacionResponse(TokenRecuperacionBase):
    id_token: int
    fecha_creacion: Optional[datetime]
    fecha_expiracion: Optional[datetime]

    class Config:
        from_attributes = True