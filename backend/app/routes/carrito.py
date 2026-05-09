from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.carrito import Carrito
from app.schemas.carrito import (
    CarritoCreate,
    CarritoUpdate,
    CarritoResponse
)

router = APIRouter(
    prefix="/carritos",
    tags=["Carritos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CarritoResponse)
def crear_carrito(
    carrito: CarritoCreate,
    db: Session = Depends(get_db)
):

    nuevo = Carrito(
        id_usuario=carrito.id_usuario,
        estado=carrito.estado,
        fecha_creacion=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[CarritoResponse])
def listar_carritos(
    db: Session = Depends(get_db)
):

    return db.query(Carrito).all()


@router.get("/{id_carrito}", response_model=CarritoResponse)
def obtener_carrito(
    id_carrito: int,
    db: Session = Depends(get_db)
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    return carrito


@router.put("/{id_carrito}", response_model=CarritoResponse)
def actualizar_carrito(
    id_carrito: int,
    datos: CarritoUpdate,
    db: Session = Depends(get_db)
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(carrito, key, value)

    db.commit()
    db.refresh(carrito)

    return carrito


@router.delete("/{id_carrito}")
def eliminar_carrito(
    id_carrito: int,
    db: Session = Depends(get_db)
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    db.delete(carrito)
    db.commit()

    return {
        "message": "Carrito eliminado"
    }