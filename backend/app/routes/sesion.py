from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.sesion import Sesion
from app.models.user import Usuario

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


# =========================
# VALIDAR ACCESO SESION
# =========================

def validar_acceso_sesion(
    sesion: Sesion,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    if sesion.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR SESION
# =========================

@router.post("/", response_model=SesionResponse)
def crear_sesion(
    sesion: SesionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
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


# =========================
# LISTAR SESIONES
# =========================

@router.get("/", response_model=list[SesionResponse])
def listar_sesiones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Sesion).all()

    return db.query(Sesion).filter(
        Sesion.id_usuario == current_user.id_usuario
    ).all()


# =========================
# OBTENER SESION
# =========================

@router.get("/{id_sesion}", response_model=SesionResponse)
def obtener_sesion(
    id_sesion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    validar_acceso_sesion(
        sesion,
        current_user
    )

    return sesion


# =========================
# ACTUALIZAR SESION
# =========================

@router.put("/{id_sesion}", response_model=SesionResponse)
def actualizar_sesion(
    id_sesion: int,
    datos: SesionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    validar_acceso_sesion(
        sesion,
        current_user
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(sesion, key, value)

    db.commit()
    db.refresh(sesion)

    return sesion


# =========================
# ELIMINAR SESION
# =========================

@router.delete("/{id_sesion}")
def eliminar_sesion(
    id_sesion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    sesion = db.query(Sesion).filter(
        Sesion.id_sesion == id_sesion
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )

    validar_acceso_sesion(
        sesion,
        current_user
    )

    db.delete(sesion)
    db.commit()

    return {
        "message": "Sesión eliminada"
    }