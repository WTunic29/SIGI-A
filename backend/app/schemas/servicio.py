from typing import Optional
from pydantic import BaseModel


class ServicioCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    duracion_minutos: int
    precio: float
    imagen_url: Optional[str] = None