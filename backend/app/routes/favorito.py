from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.favorito import Favorito
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


@router.post("/", response_model=FavoritoResponse)
def crear_favorito(
    favorito: FavoritoCreate,
    db: Session = Depends(get_db)
):

    nuevo = Favorito(
        id_usuario=favorito.id_usuario,
        id_negocio=favorito.id_negocio,
        fecha=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[FavoritoResponse])
def listar_favoritos(
    db: Session = Depends(get_db)
):

    return db.query(Favorito).all()


@router.get("/{id_favorito}", response_model=FavoritoResponse)
def obtener_favorito(
    id_favorito: int,
    db: Session = Depends(get_db)
):

    favorito = db.query(Favorito).filter(
        Favorito.id_favorito == id_favorito
    ).first()

    if not favorito:
        raise HTTPException(
            status_code=404,
            detail="Favorito no encontrado"
        )

    return favorito


@router.delete("/{id_favorito}")
def eliminar_favorito(
    id_favorito: int,
    db: Session = Depends(get_db)
):

    favorito = db.query(Favorito).filter(
        Favorito.id_favorito == id_favorito
    ).first()

    if not favorito:
        raise HTTPException(
            status_code=404,
            detail="Favorito no encontrado"
        )

    db.delete(favorito)
    db.commit()

    return {
        "message": "Favorito eliminado"
    }