from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.auditoria import Auditoria
from app.schemas.auditoria import (
    AuditoriaCreate,
    AuditoriaResponse
)

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AuditoriaResponse)
def crear_log(
    auditoria: AuditoriaCreate,
    db: Session = Depends(get_db)
):

    nuevo = Auditoria(
        id_usuario=auditoria.id_usuario,
        accion=auditoria.accion,
        tabla_afectada=auditoria.tabla_afectada,
        id_registro=auditoria.id_registro,
        detalle=auditoria.detalle,
        fecha=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[AuditoriaResponse])
def listar_logs(
    db: Session = Depends(get_db)
):

    return db.query(Auditoria).all()


@router.get("/{id_auditoria}", response_model=AuditoriaResponse)
def obtener_log(
    id_auditoria: int,
    db: Session = Depends(get_db)
):

    log = db.query(Auditoria).filter(
        Auditoria.id_auditoria == id_auditoria
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Log no encontrado"
        )

    return log


@router.delete("/{id_auditoria}")
def eliminar_log(
    id_auditoria: int,
    db: Session = Depends(get_db)
):

    log = db.query(Auditoria).filter(
        Auditoria.id_auditoria == id_auditoria
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Log no encontrado"
        )

    db.delete(log)
    db.commit()

    return {
        "message": "Log eliminado"
    }