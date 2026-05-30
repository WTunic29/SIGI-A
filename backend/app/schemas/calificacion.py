from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional


class CalificacionCreate(BaseModel):
    id_cliente: Optional[int] = None
    id_negocio: int
    id_cita: int
    puntuacion: int
    comentario: Optional[str] = None


class CalificacionUpdate(BaseModel):
    puntuacion: Optional[int] = None
    comentario: Optional[str] = None


class CalificacionResponse(BaseModel):
    id_calificacion: int
    id_cliente: int
    id_negocio: int
    id_cita: int
    puntuacion: int
    comentario: Optional[str]
    fecha: datetime

    class Config:
        from_attributes = True


class CitaPendienteCalificacion(BaseModel):
    id_cita: int
    id_negocio: int
    id_empleado: int
    negocio_nombre: str
    empleado_nombre: str
    empleado_apellido: str
    servicio_nombre: str
    servicio_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time

    class Config:
        from_attributes = True


class RankingNegocio(BaseModel):
    posicion: int
    id_negocio: int
    nombre_negocio: str
    promedio: float
    total_calificaciones: int

    class Config:
        from_attributes = True