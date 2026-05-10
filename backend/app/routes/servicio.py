from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.servicio import Servicio
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.servicio import (
    ServicioCreate,
    ServicioUpdate,
    ServicioResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO SERVICIO
# =========================

def validar_acceso_servicio(
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

    if servicio.id_negocio != negocio.id_negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR SERVICIO
# =========================

@router.post("/", response_model=ServicioResponse, status_code=201)
def crear_servicio(
    servicio: ServicioCreate,
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    ),
    db: Session = Depends(get_db)
):

    # NEGOCIO
    if current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="No tienes un negocio registrado"
            )

        id_negocio = negocio.id_negocio

    # ADMIN
    else:
        id_negocio = servicio.id_negocio

    nuevo_servicio = Servicio(
        id_negocio=id_negocio,
        nombre=servicio.nombre,
        descripcion=servicio.descripcion,
        duracion_minutos=servicio.duracion_minutos,
        precio=servicio.precio,
        estado="activo",
        imagen_url=servicio.imagen_url
    )

    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return nuevo_servicio


# =========================
# LISTAR SERVICIOS
# =========================

@router.get("/", response_model=list[ServicioResponse])
def listar_servicios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Servicio).all()

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

        return db.query(Servicio).filter(
            Servicio.id_negocio == negocio.id_negocio
        ).all()

    # CLIENTE
    return db.query(Servicio).filter(
        Servicio.estado == "activo"
    ).all()


# =========================
# OBTENER SERVICIO
# =========================

@router.get("/{id_servicio}", response_model=ServicioResponse)
def obtener_servicio(
    id_servicio: int,
    db: Session = Depends(get_db)
):

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    return servicio


# =========================
# ACTUALIZAR SERVICIO
# =========================

@router.put("/{id_servicio}", response_model=ServicioResponse)
def actualizar_servicio(
    id_servicio: int,
    datos: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    validar_acceso_servicio(
        servicio,
        current_user,
        db
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(servicio, key, value)

    db.commit()
    db.refresh(servicio)

    return servicio


# =========================
# ELIMINAR SERVICIO
# =========================

@router.delete("/{id_servicio}")
def eliminar_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    validar_acceso_servicio(
        servicio,
        current_user,
        db
    )

    servicio.estado = "inactivo"

    db.commit()

    return {
        "message": "Servicio eliminado correctamente"
    }