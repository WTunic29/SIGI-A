from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.calificacion import Calificacion
from app.schemas.calificacion import (
    CalificacionCreate,
    CalificacionUpdate,
    CalificacionResponse
)

router = APIRouter()


@router.post("/", response_model=CalificacionResponse)
def crear_calificacion(
    calificacion: CalificacionCreate,
    db: Session = Depends(get_db)
):
    if calificacion.puntuacion < 1 or calificacion.puntuacion > 5:
        raise HTTPException(
            status_code=400,
            detail="La puntuación debe estar entre 1 y 5"
        )

    nueva_calificacion = Calificacion(
        id_cliente=calificacion.id_cliente,
        id_negocio=calificacion.id_negocio,
        id_cita=calificacion.id_cita,
        puntuacion=calificacion.puntuacion,
        comentario=calificacion.comentario
    )

    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)

    return nueva_calificacion


@router.get("/negocio/{id_negocio}", response_model=List[CalificacionResponse])
def listar_calificaciones_negocio(
    id_negocio: int,
    db: Session = Depends(get_db)
):
    return db.query(Calificacion).filter(
        Calificacion.id_negocio == id_negocio
    ).all()


@router.get("/cliente/{id_cliente}", response_model=List[CalificacionResponse])
def listar_calificaciones_cliente(
    id_cliente: int,
    db: Session = Depends(get_db)
):
    return db.query(Calificacion).filter(
        Calificacion.id_cliente == id_cliente
    ).all()


@router.put("/{id_calificacion}", response_model=CalificacionResponse)
def actualizar_calificacion(
    id_calificacion: int,
    calificacion: CalificacionUpdate,
    db: Session = Depends(get_db)
):
    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    datos = calificacion.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(calificacion_db, campo, valor)

    db.commit()
    db.refresh(calificacion_db)

    return calificacion_db


@router.delete("/{id_calificacion}")
def eliminar_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_db)
):
    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    db.delete(calificacion_db)
    db.commit()

    return {"message": "Calificación eliminada correctamente"}