from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.models.cita import Cita
from app.models.horario_empleado import HorarioEmpleado
from app.models.empleado_servicio import EmpleadoServicio

from app.schemas.empleado import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO EMPLEADO
# =========================

def validar_acceso_empleado(
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
# CREAR EMPLEADO
# =========================

@router.post("/", response_model=EmpleadoResponse)
def crear_empleado(
    empleado: EmpleadoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    # NEGOCIO
    if current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        id_negocio = negocio.id_negocio

    # ADMIN
    else:
        id_negocio = empleado.id_negocio

    nuevo_empleado = Empleado(
        id_negocio=id_negocio,
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


# =========================
# LISTAR EMPLEADOS
# =========================

@router.get("/", response_model=List[EmpleadoResponse])
def listar_empleados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Empleado).all()

    # NEGOCIO
    if current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        return db.query(Empleado).filter(
            Empleado.id_negocio == negocio.id_negocio
        ).all()

    # CLIENTE
    return db.query(Empleado).filter(
        Empleado.estado == "activo"
    ).all()


# =========================
# OBTENER EMPLEADO
# =========================

@router.get("/{id_empleado}", response_model=EmpleadoResponse)
def obtener_empleado(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
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

    validar_acceso_empleado(
        empleado,
        current_user,
        db
    )

    return empleado

# =========================
# ACTUALIZAR EMPLEADO
# =========================

@router.put("/{id_empleado}", response_model=EmpleadoResponse)
def actualizar_empleado(
    id_empleado: int,
    empleado: EmpleadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    empleado_db = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado_db:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    validar_acceso_empleado(
        empleado_db,
        current_user,
        db
    )

    datos = empleado.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(empleado_db, campo, valor)

    db.commit()
    db.refresh(empleado_db)

    return empleado_db


# =========================
# ELIMINAR EMPLEADO
# =========================

@router.delete("/{id_empleado}")
def eliminar_empleado(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):
    empleado_db = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado_db:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    validar_acceso_empleado(
        empleado_db,
        current_user,
        db
    )

    # 1. Eliminar horarios del empleado
    db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_empleado == id_empleado
    ).delete(synchronize_session=False)

    # 2. Eliminar relación empleado-servicio, si existe
    db.query(EmpleadoServicio).filter(
        EmpleadoServicio.id_empleado == id_empleado
    ).delete(synchronize_session=False)

    # 3. Eliminar citas asociadas al empleado
    db.query(Cita).filter(
        Cita.id_empleado == id_empleado
    ).delete(synchronize_session=False)

    # 4. Eliminar empleado definitivamente
    db.delete(empleado_db)

    db.commit()

    return {
        "message": "Empleado, horarios, servicios asociados y citas eliminados correctamente"
    }