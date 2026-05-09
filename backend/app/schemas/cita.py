from pydantic import BaseModel
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional


class CitaCreate(BaseModel):
    id_cliente: int
    id_negocio: int
    id_empleado: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    observaciones: Optional[str] = None


class CitaUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class CitaResponse(BaseModel):
    id_cita: int
    id_cliente: int
    id_negocio: int
    id_empleado: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: str
    observaciones: Optional[str]
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class DetalleCitaCreate(BaseModel):
    id_servicio: int
    precio: Decimal
    duracion: int


class DetalleCitaResponse(BaseModel):
    id_detalle_cita: int
    id_cita: int
    id_servicio: int
    precio: Decimal
    duracion: int

    class Config:
        from_attributes = True