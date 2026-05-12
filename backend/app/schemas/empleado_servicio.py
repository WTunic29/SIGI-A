from pydantic import BaseModel


class EmpleadoServicioCreate(BaseModel):
    id_empleado: int
    id_servicio: int


class EmpleadoServicioResponse(BaseModel):
    id_empleado_servicio: int
    id_empleado: int
    id_servicio: int

    class Config:
        from_attributes = True