from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.horario_empleado import HorarioEmpleado
from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.horario_empleado import (
    HorarioEmpleadoCreate,
    HorarioEmpleadoUpdate,
    HorarioEmpleadoResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO HORARIO
# =========================

def validar_acceso_horario(
    empleado: Empleado,
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


# =========================
# CREAR HORARIO
# =========================

@router.post("/", response_model=HorarioEmpleadoResponse)
def crear_horario(
    horario: HorarioEmpleadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == horario.id_empleado
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    validar_acceso_horario(
        empleado,
        current_user,
        db
    )

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


# =========================
# LISTAR HORARIOS
# =========================

@router.get("/{id_empleado}")
def listar_horarios_empleado(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    if current_user.rol == "negocio":
        validar_acceso_horario(
            empleado,
            current_user,
            db
        )

    horarios = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_empleado == id_empleado
    ).all()

    return {
        "empleado": {
            "id_empleado": empleado.id_empleado,
            "nombre": empleado.nombre,
            "apellido": empleado.apellido,
            "especialidad": empleado.especialidad
        },
        "horarios": horarios
    }

# =========================
# ACTUALIZAR HORARIO
# =========================

@router.put("/{id_horario}", response_model=HorarioEmpleadoResponse)
def actualizar_horario(
    id_horario: int,
    horario: HorarioEmpleadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    horario_db = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_horario == id_horario
    ).first()

    if not horario_db:
        raise HTTPException(
            status_code=404,
            detail="Horario no encontrado"
        )

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == horario_db.id_empleado
    ).first()

    validar_acceso_horario(
        empleado,
        current_user,
        db
    )

    datos = horario.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(horario_db, campo, valor)

    db.commit()
    db.refresh(horario_db)

    return horario_db


# =========================
# ELIMINAR HORARIO
# =========================

@router.delete("/{id_horario}")
def eliminar_horario(
    id_horario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    horario_db = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_horario == id_horario
    ).first()

    if not horario_db:
        raise HTTPException(
            status_code=404,
            detail="Horario no encontrado"
        )

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == horario_db.id_empleado
    ).first()

    validar_acceso_horario(
        empleado,
        current_user,
        db
    )

    db.delete(horario_db)
    db.commit()

    return {
        "message": "Horario eliminado correctamente"
    }