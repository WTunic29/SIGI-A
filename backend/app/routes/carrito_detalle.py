from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.carrito_detalle import CarritoDetalle
from app.schemas.carrito_detalle import (
    CarritoDetalleCreate,
    CarritoDetalleUpdate,
    CarritoDetalleResponse
)

router = APIRouter(
    prefix="/carrito-detalle",
    tags=["Carrito Detalle"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CarritoDetalleResponse)
def crear_detalle(
    detalle: CarritoDetalleCreate,
    db: Session = Depends(get_db)
):

    nuevo = CarritoDetalle(**detalle.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[CarritoDetalleResponse])
def listar_detalles(
    db: Session = Depends(get_db)
):

    return db.query(CarritoDetalle).all()


@router.get("/{id_detalle}", response_model=CarritoDetalleResponse)
def obtener_detalle(
    id_detalle: int,
    db: Session = Depends(get_db)
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    return detalle


@router.put("/{id_detalle}", response_model=CarritoDetalleResponse)
def actualizar_detalle(
    id_detalle: int,
    datos: CarritoDetalleUpdate,
    db: Session = Depends(get_db)
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(detalle, key, value)

    db.commit()
    db.refresh(detalle)

    return detalle


@router.delete("/{id_detalle}")
def eliminar_detalle(
    id_detalle: int,
    db: Session = Depends(get_db)
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    db.delete(detalle)
    db.commit()

    return {
        "message": "Detalle eliminado"
    }