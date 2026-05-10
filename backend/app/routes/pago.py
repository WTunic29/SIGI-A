from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.negocio import Negocio
from app.models.user import Usuario

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
# VALIDAR ACCESO PAGO
# =========================

def validar_acceso_pago(
    pago: Pago,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if current_user.rol == "cliente":

        pedido = db.query(Pedido).filter(
            Pedido.id_pedido == pago.id_pedido
        ).first()

        if not pedido or pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    # NEGOCIO
    elif current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        pedido = db.query(Pedido).filter(
            Pedido.id_pedido == pago.id_pedido
        ).first()

        if not pedido or pedido.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )


# =========================
# CREAR PAGO
# =========================

@router.post("/", response_model=PagoResponse)
def crear_pago(
    pago: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == pago.id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    # CLIENTE SOLO SUS PEDIDOS
    if current_user.rol == "cliente":

        if pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    # NEGOCIO SOLO SUS PEDIDOS
    elif current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        if pedido.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Pago).all()

    # CLIENTE
    if current_user.rol == "cliente":

        pagos = (
            db.query(Pago)
            .join(Pedido, Pedido.id_pedido == Pago.id_pedido)
            .filter(
                Pedido.id_usuario == current_user.id_usuario
            )
            .all()
        )

        return pagos

    # NEGOCIO
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    pagos = (
        db.query(Pago)
        .join(Pedido, Pedido.id_pedido == Pago.id_pedido)
        .filter(
            Pedido.id_negocio == negocio.id_negocio
        )
        .all()
    )

    return pagos


# =========================
# OBTENER PAGO
# =========================

@router.get("/{id_pago}", response_model=PagoResponse)
def obtener_pago(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    validar_acceso_pago(
        pago,
        current_user,
        db
    )

    return pago


# =========================
# ACTUALIZAR PAGO
# =========================

@router.put("/{id_pago}", response_model=PagoResponse)
def actualizar_pago(
    id_pago: int,
    datos: PagoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    validar_acceso_pago(
        pago,
        current_user,
        db
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
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