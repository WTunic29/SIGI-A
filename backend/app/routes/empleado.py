from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.empleado import Empleado
from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoResponse

router = APIRouter()


@router.post("/", response_model=EmpleadoResponse)
def crear_empleado(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    nuevo_empleado = Empleado(
        id_negocio=empleado.id_negocio,
        nombre=empleado.nombre,
        apellido=empleado.apellido,
        telefono=empleado.telefono,
        email=empleado.email,
        especialidad=empleado.especialidad,
        foto_url=empleado.foto_url,
        estado="activo"
    )

    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)

    return nuevo_empleado


@router.get("/{id_negocio}", response_model=List[EmpleadoResponse])
def listar_empleados_por_negocio(id_negocio: int, db: Session = Depends(get_db)):
    empleados = db.query(Empleado).filter(
        Empleado.id_negocio == id_negocio
    ).all()

    return empleados


@router.put("/{id_empleado}", response_model=EmpleadoResponse)
def actualizar_empleado(
    id_empleado: int,
    empleado: EmpleadoUpdate,
    db: Session = Depends(get_db)
):
    empleado_db = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    datos = empleado.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(empleado_db, campo, valor)

    db.commit()
    db.refresh(empleado_db)

    return empleado_db


@router.delete("/{id_empleado}")
def eliminar_empleado(id_empleado: int, db: Session = Depends(get_db)):
    empleado_db = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    empleado_db.estado = "inactivo"

    db.commit()

    return {"message": "Empleado desactivado correctamente"}