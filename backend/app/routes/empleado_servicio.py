from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.empleado_servicio import EmpleadoServicio
from app.schemas.empleado_servicio import EmpleadoServicioCreate, EmpleadoServicioResponse

router = APIRouter()


@router.post("/", response_model=EmpleadoServicioResponse)
def asignar_servicio_a_empleado(
    asignacion: EmpleadoServicioCreate,
    db: Session = Depends(get_db)
):
    existente = db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado == asignacion.id_empleado,
        EmpleadoServicio.id_servicio == asignacion.id_servicio
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Este servicio ya está asignado al empleado"
        )

    nueva_asignacion = EmpleadoServicio(
        id_empleado=asignacion.id_empleado,
        id_servicio=asignacion.id_servicio
    )

    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)

    return nueva_asignacion


@router.get("/{id_empleado}", response_model=List[EmpleadoServicioResponse])
def listar_servicios_de_empleado(
    id_empleado: int,
    db: Session = Depends(get_db)
):
    servicios = db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado == id_empleado
    ).all()

    return servicios


@router.delete("/{id_empleado_servicio}")
def eliminar_servicio_de_empleado(
    id_empleado_servicio: int,
    db: Session = Depends(get_db)
):
    asignacion = db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado_servicio == id_empleado_servicio
    ).first()

    if not asignacion:
        raise HTTPException(
            status_code=404,
            detail="Asignación no encontrada"
        )

    db.delete(asignacion)
    db.commit()

    return {"message": "Servicio eliminado del empleado correctamente"}