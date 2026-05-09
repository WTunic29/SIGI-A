from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.pedido_detalle import PedidoDetalle
from app.schemas.pedido_detalle import (
    PedidoDetalleCreate,
    PedidoDetalleUpdate,
    PedidoDetalleResponse
)

router = APIRouter(
    prefix="/pedido-detalle",
    tags=["Pedido Detalle"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PedidoDetalleResponse)
def crear_detalle(
    detalle: PedidoDetalleCreate,
    db: Session = Depends(get_db)
):

    nuevo = PedidoDetalle(**detalle.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[PedidoDetalleResponse])
def listar_detalles(
    db: Session = Depends(get_db)
):

    return db.query(PedidoDetalle).all()


@router.get("/{id_detalle}", response_model=PedidoDetalleResponse)
def obtener_detalle(
    id_detalle: int,
    db: Session = Depends(get_db)
):

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    return detalle


@router.put("/{id_detalle}", response_model=PedidoDetalleResponse)
def actualizar_detalle(
    id_detalle: int,
    datos: PedidoDetalleUpdate,
    db: Session = Depends(get_db)
):

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
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

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
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