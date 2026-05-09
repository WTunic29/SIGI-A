from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.token_recuperacion import TokenRecuperacion
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


@router.post("/", response_model=TokenRecuperacionResponse)
def crear_token(
    token_data: TokenRecuperacionCreate,
    db: Session = Depends(get_db)
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


@router.get("/", response_model=list[TokenRecuperacionResponse])
def listar_tokens(
    db: Session = Depends(get_db)
):

    return db.query(TokenRecuperacion).all()


@router.get("/{id_token}", response_model=TokenRecuperacionResponse)
def obtener_token(
    id_token: int,
    db: Session = Depends(get_db)
):

    token = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.id_token == id_token
    ).first()

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Token no encontrado"
        )

    return token


@router.delete("/{id_token}")
def eliminar_token(
    id_token: int,
    db: Session = Depends(get_db)
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