from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.sesion import Sesion
from app.schemas.sesion import (
    SesionCreate,
    SesionUpdate,
    SesionResponse
)

router = APIRouter(
    prefix="/sesiones",
    tags=["Sesiones"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SesionResponse)
def crear_sesion(
    sesion: SesionCreate,
    db: Session = Depends(get_db)
):

    nueva = Sesion(
        id_usuario=sesion.id_usuario,
        token=sesion.token,
        fecha_inicio=datetime.utcnow(),
        fecha_expiracion=sesion.fecha_expiracion,
        ip=sesion.ip,
        user_agent=sesion.user_agent,
        activa=sesion.activa
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@router.get("/", response_model=list[SesionResponse])
def listar_sesiones(
    db: Session = Depends(get_db)
):

    return db.query(Sesion).all()


@router.get("/{id_sesion}", response_model=SesionResponse)
def obtener_sesion(
    id_sesion: int,
    db: Session = Depends(get_db)
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    return sesion


@router.put("/{id_sesion}", response_model=SesionResponse)
def actualizar_sesion(
    id_sesion: int,
    datos: SesionUpdate,
    db: Session = Depends(get_db)
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(sesion, key, value)

    db.commit()
    db.refresh(sesion)

    return sesion


@router.delete("/{id_sesion}")
def eliminar_sesion(
    id_sesion: int,
    db: Session = Depends(get_db)
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    db.delete(sesion)
    db.commit()

    return {
        "message": "Sesión eliminada"
    }