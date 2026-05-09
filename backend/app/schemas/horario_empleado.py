from pydantic import BaseModel
from datetime import time
from typing import Optional


class HorarioEmpleadoCreate(BaseModel):
    id_empleado: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    disponible: Optional[bool] = True


class HorarioEmpleadoUpdate(BaseModel):
    dia_semana: Optional[int] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    disponible: Optional[bool] = None


class HorarioEmpleadoResponse(BaseModel):
    id_horario: int
    id_empleado: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    disponible: bool

    class Config:
        from_attributes = True