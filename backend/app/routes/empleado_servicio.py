from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.empleado_servicio import EmpleadoServicio
from app.models.empleado import Empleado
from app.models.servicio import Servicio
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.empleado_servicio import (
    EmpleadoServicioCreate,
    EmpleadoServicioResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO
# =========================

def validar_acceso_asignacion(
    empleado: Empleado,
    servicio: Servicio,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    if empleado.id_negocio != negocio.id_negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

    if servicio.id_negocio != negocio.id_negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# ASIGNAR SERVICIO
# =========================

@router.post("/", response_model=EmpleadoServicioResponse)
def asignar_servicio_a_empleado(
    asignacion: EmpleadoServicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == asignacion.id_empleado
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == asignacion.id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    validar_acceso_asignacion(
        empleado,
        servicio,
        current_user,
        db
    )

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


# =========================
# LISTAR SERVICIOS EMPLEADO
# =========================

@router.get("/{id_empleado}", response_model=List[EmpleadoServicioResponse])
def listar_servicios_de_empleado(
    id_empleado: int,
    db: Session = Depends(get_db)
):

    servicios = db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado == id_empleado
    ).all()

    return servicios


# =========================
# ELIMINAR ASIGNACION
# =========================

@router.delete("/{id_empleado_servicio}")
def eliminar_servicio_de_empleado(
    id_empleado_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    asignacion = db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado_servicio == id_empleado_servicio
    ).first()

    if not asignacion:
        raise HTTPException(
            status_code=404,
            detail="Asignación no encontrada"
        )

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == asignacion.id_empleado
    ).first()

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == asignacion.id_servicio
    ).first()

    validar_acceso_asignacion(
        empleado,
        servicio,
        current_user,
        db
    )

    db.delete(asignacion)
    db.commit()

    return {
        "message": "Servicio eliminado del empleado correctamente"
    }