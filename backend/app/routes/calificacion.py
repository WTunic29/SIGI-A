from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.calificacion import Calificacion
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.calificacion import (
    CalificacionCreate,
    CalificacionUpdate,
    CalificacionResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO
# =========================

def validar_acceso_calificacion(
    calificacion: Calificacion,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if current_user.rol == "cliente":

        if calificacion.id_cliente != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    # NEGOCIO
    elif current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        if calificacion.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )


# =========================
# CREAR CALIFICACION
# =========================

@router.post("/", response_model=CalificacionResponse)
def crear_calificacion(
    calificacion: CalificacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    if calificacion.puntuacion < 1 or calificacion.puntuacion > 5:
        raise HTTPException(
            status_code=400,
            detail="La puntuación debe estar entre 1 y 5"
        )

    # CLIENTE
    if current_user.rol == "cliente":

        id_cliente = current_user.id_usuario

    # ADMIN
    else:
        id_cliente = calificacion.id_cliente

    nueva_calificacion = Calificacion(
        id_cliente=id_cliente,
        id_negocio=calificacion.id_negocio,
        id_cita=calificacion.id_cita,
        puntuacion=calificacion.puntuacion,
        comentario=calificacion.comentario
    )

    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)

    return nueva_calificacion


# =========================
# LISTAR CALIFICACIONES
# =========================

@router.get("/", response_model=List[CalificacionResponse])
def listar_calificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Calificacion).all()

    # CLIENTE
    if current_user.rol == "cliente":

        return db.query(Calificacion).filter(
            Calificacion.id_cliente == current_user.id_usuario
        ).all()

    # NEGOCIO
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return db.query(Calificacion).filter(
        Calificacion.id_negocio == negocio.id_negocio
    ).all()


# =========================
# OBTENER CALIFICACION
# =========================

@router.get("/{id_calificacion}", response_model=CalificacionResponse)
def obtener_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    calificacion = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion,
        current_user,
        db
    )

    return calificacion


# =========================
# ACTUALIZAR CALIFICACION
# =========================

@router.put("/{id_calificacion}", response_model=CalificacionResponse)
def actualizar_calificacion(
    id_calificacion: int,
    calificacion: CalificacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion_db,
        current_user,
        db
    )

    datos = calificacion.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(calificacion_db, campo, valor)

    db.commit()
    db.refresh(calificacion_db)

    return calificacion_db


# =========================
# ELIMINAR CALIFICACION
# =========================

@router.delete("/{id_calificacion}")
def eliminar_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion_db,
        current_user,
        db
    )

    db.delete(calificacion_db)
    db.commit()

    return {
        "message": "Calificación eliminada correctamente"
    }