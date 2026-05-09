from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notificacion import Notificacion
from app.schemas.notificacion import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionResponse
)

router = APIRouter()


@router.post("/", response_model=NotificacionResponse)
def crear_notificacion(
    notificacion: NotificacionCreate,
    db: Session = Depends(get_db)
):
    nueva_notificacion = Notificacion(
        id_usuario=notificacion.id_usuario,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        tipo=notificacion.tipo,
        leida=False
    )

    db.add(nueva_notificacion)
    db.commit()
    db.refresh(nueva_notificacion)

    return nueva_notificacion


@router.get("/usuario/{id_usuario}", response_model=List[NotificacionResponse])
def listar_notificaciones_usuario(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return db.query(Notificacion).filter(
        Notificacion.id_usuario == id_usuario
    ).all()


@router.get("/usuario/{id_usuario}/no-leidas", response_model=List[NotificacionResponse])
def listar_notificaciones_no_leidas(
    id_usuario: int,
    db: Session = Depends(get_db)
):
    return db.query(Notificacion).filter(
        Notificacion.id_usuario == id_usuario,
        Notificacion.leida == False
    ).all()


@router.put("/{id_notificacion}/leer", response_model=NotificacionResponse)
def marcar_como_leida(
    id_notificacion: int,
    db: Session = Depends(get_db)
):
    notificacion_db = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()

    if not notificacion_db:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notificacion_db.leida = True

    db.commit()
    db.refresh(notificacion_db)

    return notificacion_db


@router.delete("/{id_notificacion}")
def eliminar_notificacion(
    id_notificacion: int,
    db: Session = Depends(get_db)
):
    notificacion_db = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()

    if not notificacion_db:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    db.delete(notificacion_db)
    db.commit()

    return {"message": "Notificación eliminada correctamente"}