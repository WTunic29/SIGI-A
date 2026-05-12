from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.notificacion import Notificacion
from app.models.user import Usuario

from app.schemas.notificacion import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO
# =========================

def validar_acceso_notificacion(
    notificacion: Notificacion,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    if notificacion.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR NOTIFICACION
# =========================

@router.post("/", response_model=NotificacionResponse)
def crear_notificacion(
    notificacion: NotificacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
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


# =========================
# LISTAR NOTIFICACIONES
# =========================

@router.get("/", response_model=List[NotificacionResponse])
def listar_notificaciones_usuario(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Notificacion).all()

    return db.query(Notificacion).filter(
        Notificacion.id_usuario == current_user.id_usuario
    ).all()


# =========================
# LISTAR NO LEIDAS
# =========================

@router.get("/no-leidas", response_model=List[NotificacionResponse])
def listar_notificaciones_no_leidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":

        return db.query(Notificacion).filter(
            Notificacion.leida == False
        ).all()

    return db.query(Notificacion).filter(
        Notificacion.id_usuario == current_user.id_usuario,
        Notificacion.leida == False
    ).all()


# =========================
# MARCAR LEIDA
# =========================

@router.put("/{id_notificacion}/leer", response_model=NotificacionResponse)
def marcar_como_leida(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    notificacion_db = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()

    if not notificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Notificación no encontrada"
        )

    validar_acceso_notificacion(
        notificacion_db,
        current_user
    )

    notificacion_db.leida = True

    db.commit()
    db.refresh(notificacion_db)

    return notificacion_db


# =========================
# ELIMINAR
# =========================

@router.delete("/{id_notificacion}")
def eliminar_notificacion(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    notificacion_db = db.query(Notificacion).filter(
        Notificacion.id_notificacion == id_notificacion
    ).first()

    if not notificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Notificación no encontrada"
        )

    validar_acceso_notificacion(
        notificacion_db,
        current_user
    )

    db.delete(notificacion_db)
    db.commit()

    return {
        "message": "Notificación eliminada correctamente"
    }