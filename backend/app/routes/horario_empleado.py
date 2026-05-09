from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.horario_empleado import HorarioEmpleado
from app.schemas.horario_empleado import (
    HorarioEmpleadoCreate,
    HorarioEmpleadoUpdate,
    HorarioEmpleadoResponse
)

router = APIRouter()


@router.post("/", response_model=HorarioEmpleadoResponse)
def crear_horario(horario: HorarioEmpleadoCreate, db: Session = Depends(get_db)):
    nuevo_horario = HorarioEmpleado(
        id_empleado=horario.id_empleado,
        dia_semana=horario.dia_semana,
        hora_inicio=horario.hora_inicio,
        hora_fin=horario.hora_fin,
        disponible=horario.disponible
    )

    db.add(nuevo_horario)
    db.commit()
    db.refresh(nuevo_horario)

    return nuevo_horario


@router.get("/{id_empleado}", response_model=List[HorarioEmpleadoResponse])
def listar_horarios_empleado(id_empleado: int, db: Session = Depends(get_db)):
    horarios = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_empleado == id_empleado
    ).all()

    return horarios


@router.put("/{id_horario}", response_model=HorarioEmpleadoResponse)
def actualizar_horario(
    id_horario: int,
    horario: HorarioEmpleadoUpdate,
    db: Session = Depends(get_db)
):
    horario_db = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_horario == id_horario
    ).first()

    if not horario_db:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    datos = horario.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(horario_db, campo, valor)

    db.commit()
    db.refresh(horario_db)

    return horario_db


@router.delete("/{id_horario}")
def eliminar_horario(id_horario: int, db: Session = Depends(get_db)):
    horario_db = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_horario == id_horario
    ).first()

    if not horario_db:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    db.delete(horario_db)
    db.commit()

    return {"message": "Horario eliminado correctamente"}