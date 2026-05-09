from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.pedido import Pedido
from app.schemas.pedido import (
    PedidoCreate,
    PedidoUpdate,
    PedidoResponse
)

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PedidoResponse)
def crear_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db)
):

    nuevo_pedido = Pedido(
        id_usuario=pedido.id_usuario,
        id_negocio=pedido.id_negocio,
        total=pedido.total,
        estado=pedido.estado,
        fecha=datetime.utcnow()
    )

    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    return nuevo_pedido


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    db: Session = Depends(get_db)
):

    return db.query(Pedido).all()


@router.get("/{id_pedido}", response_model=PedidoResponse)
def obtener_pedido(
    id_pedido: int,
    db: Session = Depends(get_db)
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return pedido


@router.put("/{id_pedido}", response_model=PedidoResponse)
def actualizar_pedido(
    id_pedido: int,
    datos: PedidoUpdate,
    db: Session = Depends(get_db)
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(pedido, key, value)

    db.commit()
    db.refresh(pedido)

    return pedido


@router.delete("/{id_pedido}")
def eliminar_pedido(
    id_pedido: int,
    db: Session = Depends(get_db)
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    db.delete(pedido)
    db.commit()

    return {
        "message": "Pedido eliminado"
    }