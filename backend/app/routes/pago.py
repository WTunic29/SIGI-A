from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.pago import Pago
from app.schemas.pago import (
    PagoCreate,
    PagoUpdate,
    PagoResponse
)

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)


# =========================
# DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREAR PAGO
# =========================

@router.post("/", response_model=PagoResponse)
def crear_pago(
    pago: PagoCreate,
    db: Session = Depends(get_db)
):

    nuevo_pago = Pago(
        id_pedido=pago.id_pedido,
        metodo_pago=pago.metodo_pago,
        referencia_externa=pago.referencia_externa,
        estado_pago=pago.estado_pago,
        valor=pago.valor,
        fecha_pago=datetime.utcnow(),
        respuesta_pasarela=pago.respuesta_pasarela
    )

    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)

    return nuevo_pago


# =========================
# LISTAR PAGOS
# =========================

@router.get("/", response_model=list[PagoResponse])
def listar_pagos(
    db: Session = Depends(get_db)
):

    pagos = db.query(Pago).all()

    return pagos


# =========================
# OBTENER PAGO
# =========================

@router.get("/{id_pago}", response_model=PagoResponse)
def obtener_pago(
    id_pago: int,
    db: Session = Depends(get_db)
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    return pago


# =========================
# ACTUALIZAR PAGO
# =========================

@router.put("/{id_pago}", response_model=PagoResponse)
def actualizar_pago(
    id_pago: int,
    datos: PagoUpdate,
    db: Session = Depends(get_db)
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(pago, key, value)

    db.commit()
    db.refresh(pago)

    return pago


# =========================
# ELIMINAR PAGO
# =========================

@router.delete("/{id_pago}")
def eliminar_pago(
    id_pago: int,
    db: Session = Depends(get_db)
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    db.delete(pago)
    db.commit()

    return {
        "message": "Pago eliminado correctamente"
    }