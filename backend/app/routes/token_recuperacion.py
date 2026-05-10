from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.token_recuperacion import TokenRecuperacion
from app.models.user import Usuario

from app.schemas.token_recuperacion import (
    TokenRecuperacionCreate,
    TokenRecuperacionResponse
)

router = APIRouter(
    prefix="/tokens-recuperacion",
    tags=["Tokens Recuperacion"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO TOKEN
# =========================

def validar_acceso_token(
    token: TokenRecuperacion,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    if token.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR TOKEN
# =========================

@router.post("/", response_model=TokenRecuperacionResponse)
def crear_token(
    token_data: TokenRecuperacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    nuevo = TokenRecuperacion(
        id_usuario=token_data.id_usuario,
        token=token_data.token,
        fecha_creacion=datetime.utcnow(),
        fecha_expiracion=token_data.fecha_expiracion,
        usado=token_data.usado
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR TOKENS
# =========================

@router.get("/", response_model=list[TokenRecuperacionResponse])
def listar_tokens(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(TokenRecuperacion).all()

    return db.query(TokenRecuperacion).filter(
        TokenRecuperacion.id_usuario == current_user.id_usuario
    ).all()


# =========================
# OBTENER TOKEN
# =========================

@router.get("/{id_token}", response_model=TokenRecuperacionResponse)
def obtener_token(
    id_token: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    token = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.id_token == id_token
    ).first()

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Token no encontrado"
        )

    validar_acceso_token(
        token,
        current_user
    )

    return token


# =========================
# ELIMINAR TOKEN
# =========================

@router.delete("/{id_token}")
def eliminar_token(
    id_token: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    token = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.id_token == id_token
    ).first()

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Token no encontrado"
        )

    db.delete(token)
    db.commit()

    return {
        "message": "Token eliminado"
    }