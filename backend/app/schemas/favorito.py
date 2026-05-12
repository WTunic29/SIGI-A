from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoritoBase(BaseModel):
    id_usuario: int
    id_negocio: int


class FavoritoCreate(FavoritoBase):
    pass


class FavoritoResponse(FavoritoBase):
    id_favorito: int
    fecha: Optional[datetime]

    class Config:
        from_attributes = True