from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional


class CalificacionCreate(BaseModel):
    id_cliente: Optional[int] = None
    id_negocio: int
    id_cita: int
    puntuacion: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None


class CalificacionUpdate(BaseModel):
    puntuacion: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None


class CalificacionResponse(BaseModel):
    id_calificacion: int
    id_cliente: int
    id_negocio: int
    id_cita: int
    puntuacion: int
    comentario: Optional[str] = None
    fecha: datetime

    class Config:
        from_attributes = True


class RankingNegocio(BaseModel):
    posicion: int
    id_negocio: int
    nombre_negocio: str
    promedio: float
    total_calificaciones: int


class CitaPendienteCalificacion(BaseModel):
    id_cita: int
    id_negocio: int
    id_empleado: Optional[int] = None
    negocio_nombre: str
    empleado_nombre: Optional[str] = None
    empleado_apellido: Optional[str] = None
    servicio_nombre: Optional[str] = None
    servicio_id: Optional[int] = None
    fecha: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
