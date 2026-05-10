from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.negocio import (
    NegocioCreate,
    NegocioUpdate,
    NegocioResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO NEGOCIO
# =========================

def validar_acceso_negocio(
    negocio: Negocio,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    if negocio.id_usuario_propietario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR NEGOCIO
# =========================

@router.post("/", response_model=NegocioResponse, status_code=201)
def crear_negocio(
    negocio: NegocioCreate,
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    ),
    db: Session = Depends(get_db)
):

    # NEGOCIO
    if current_user.rol == "negocio":

        existente = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if existente:
            raise HTTPException(
                status_code=400,
                detail="Este usuario ya tiene un negocio registrado"
            )

        id_usuario_propietario = current_user.id_usuario

    # ADMIN
    else:
        id_usuario_propietario = negocio.id_usuario_propietario

    nuevo_negocio = Negocio(
        id_usuario_propietario=id_usuario_propietario,
        nombre_negocio=negocio.nombre,
        descripcion=negocio.descripcion,
        direccion=negocio.direccion,
        telefono=negocio.telefono,
        email_negocio=negocio.correo
    )

    db.add(nuevo_negocio)
    db.commit()
    db.refresh(nuevo_negocio)

    return nuevo_negocio


# =========================
# LISTAR NEGOCIOS
# =========================

@router.get("/", response_model=list[NegocioResponse])
def listar_negocios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Negocio).all()

    # NEGOCIO
    if current_user.rol == "negocio":

        return db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).all()

    # CLIENTE
    return db.query(Negocio).all()


# =========================
# OBTENER NEGOCIO
# =========================

@router.get("/{id_negocio}", response_model=NegocioResponse)
def obtener_negocio(
    id_negocio: int,
    db: Session = Depends(get_db)
):

    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == id_negocio
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return negocio


# =========================
# ACTUALIZAR NEGOCIO
# =========================

@router.put("/{id_negocio}", response_model=NegocioResponse)
def actualizar_negocio(
    id_negocio: int,
    datos: NegocioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == id_negocio
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    validar_acceso_negocio(
        negocio,
        current_user
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(negocio, key, value)

    db.commit()
    db.refresh(negocio)

    return negocio


# =========================
# ELIMINAR NEGOCIO
# =========================

@router.delete("/{id_negocio}")
def eliminar_negocio(
    id_negocio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == id_negocio
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    validar_acceso_negocio(
        negocio,
        current_user
    )

    db.delete(negocio)
    db.commit()

    return {
        "message": "Negocio eliminado correctamente"
    }