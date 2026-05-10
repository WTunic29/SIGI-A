from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.favorito import Favorito
from app.models.user import Usuario

from app.schemas.favorito import (
    FavoritoCreate,
    FavoritoResponse
)

router = APIRouter(
    prefix="/favoritos",
    tags=["Favoritos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO FAVORITO
# =========================

def validar_acceso_favorito(
    favorito: Favorito,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    if favorito.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR FAVORITO
# =========================

@router.post("/", response_model=FavoritoResponse)
def crear_favorito(
    favorito: FavoritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):

    nuevo = Favorito(
        id_usuario=current_user.id_usuario,
        id_negocio=favorito.id_negocio,
        fecha=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR FAVORITOS
# =========================

@router.get("/", response_model=list[FavoritoResponse])
def listar_favoritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Favorito).all()

    return db.query(Favorito).filter(
        Favorito.id_usuario == current_user.id_usuario
    ).all()


# =========================
# OBTENER FAVORITO
# =========================

@router.get("/{id_favorito}", response_model=FavoritoResponse)
def obtener_favorito(
    id_favorito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    favorito = db.query(Favorito).filter(
        Favorito.id_favorito == id_favorito
    ).first()

    if not favorito:
        raise HTTPException(
            status_code=404,
            detail="Favorito no encontrado"
        )

    validar_acceso_favorito(
        favorito,
        current_user
    )

    return favorito


# =========================
# ELIMINAR FAVORITO
# =========================

@router.delete("/{id_favorito}")
def eliminar_favorito(
    id_favorito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    favorito = db.query(Favorito).filter(
        Favorito.id_favorito == id_favorito
    ).first()

    if not favorito:
        raise HTTPException(
            status_code=404,
            detail="Favorito no encontrado"
        )

    validar_acceso_favorito(
        favorito,
        current_user
    )

    db.delete(favorito)
    db.commit()

    return {
        "message": "Favorito eliminado"
    }