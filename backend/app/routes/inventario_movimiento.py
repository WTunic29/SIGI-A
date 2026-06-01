from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.inventario_movimiento import InventarioMovimiento
from app.models.producto import Producto
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.inventario_movimiento import (
    InventarioMovimientoCreate,
    InventarioMovimientoResponse
)

router = APIRouter()


# =========================
# VALIDAR ACCESO PRODUCTO
# =========================

def validar_acceso_producto(
    producto: Producto,
    current_user: Usuario,
    db: Session
):

    # ADMIN / SUPERADMIN
    if current_user.rol in ["admin", "superadmin"]:
        return

    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == producto.id_negocio,
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para gestionar inventario de este producto"
        )


# =========================
# CREAR MOVIMIENTO
# =========================

@router.post("/", response_model=InventarioMovimientoResponse)
def crear_movimiento(
    movimiento: InventarioMovimientoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    producto = db.query(Producto).filter(
        Producto.id_producto == movimiento.id_producto
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    validar_acceso_producto(
        producto,
        current_user,
        db
    )

    if movimiento.tipo_movimiento not in ["entrada", "salida"]:
        raise HTTPException(
            status_code=400,
            detail="Tipo movimiento inválido"
        )

    if movimiento.tipo_movimiento == "entrada":
        producto.stock += movimiento.cantidad

    if movimiento.tipo_movimiento == "salida":

        if producto.stock < movimiento.cantidad:
            raise HTTPException(
                status_code=400,
                detail="Stock insuficiente"
            )

        producto.stock -= movimiento.cantidad

    nuevo_movimiento = InventarioMovimiento(
        id_producto=movimiento.id_producto,
        tipo_movimiento=movimiento.tipo_movimiento,
        cantidad=movimiento.cantidad,
        motivo=movimiento.motivo
    )

    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)

    return nuevo_movimiento


# =========================
# LISTAR MOVIMIENTOS
# =========================

@router.get("/{id_producto}", response_model=List[InventarioMovimientoResponse])
def listar_movimientos_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    producto = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    validar_acceso_producto(
        producto,
        current_user,
        db
    )

    return db.query(InventarioMovimiento).filter(
        InventarioMovimiento.id_producto == id_producto
    ).all()