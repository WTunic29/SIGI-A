from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.producto import Producto
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse
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

    # ADMIN
    if current_user.rol == "admin":
        return

    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    if producto.id_negocio != negocio.id_negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR PRODUCTO
# =========================

@router.post("/", response_model=ProductoResponse)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    # NEGOCIO
    if current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        id_negocio = negocio.id_negocio

    # ADMIN
    else:
        id_negocio = producto.id_negocio

    nuevo_producto = Producto(
        id_negocio=id_negocio,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock=producto.stock,
        imagen_url=producto.imagen_url,
        estado="activo"
    )

    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)

    return nuevo_producto


# =========================
# LISTAR PRODUCTOS
# =========================

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Producto).all()

    # NEGOCIO
    if current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        return db.query(Producto).filter(
            Producto.id_negocio == negocio.id_negocio
        ).all()

    # CLIENTE
    return db.query(Producto).filter(
        Producto.estado == "activo"
    ).all()


# =========================
# OBTENER PRODUCTO
# =========================

@router.get("/{id_producto}", response_model=ProductoResponse)
def obtener_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):

    producto = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto


# =========================
# ACTUALIZAR PRODUCTO
# =========================

@router.put("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    producto_db = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    validar_acceso_producto(
        producto_db,
        current_user,
        db
    )

    datos = producto.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(producto_db, campo, valor)

    db.commit()
    db.refresh(producto_db)

    return producto_db


# =========================
# ELIMINAR PRODUCTO
# =========================

@router.delete("/{id_producto}")
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    producto_db = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    validar_acceso_producto(
        producto_db,
        current_user,
        db
    )

    producto_db.estado = "inactivo"

    db.commit()

    return {
        "message": "Producto desactivado correctamente"
    }