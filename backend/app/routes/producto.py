from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.producto import Producto
from app.schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse
)

router = APIRouter()


@router.post("/", response_model=ProductoResponse)
def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db)
):
    nuevo_producto = Producto(
        id_negocio=producto.id_negocio,
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


@router.get("/negocio/{id_negocio}", response_model=List[ProductoResponse])
def listar_productos_negocio(
    id_negocio: int,
    db: Session = Depends(get_db)
):
    return db.query(Producto).filter(
        Producto.id_negocio == id_negocio
    ).all()


@router.put("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db)
):
    producto_db = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    datos = producto.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(producto_db, campo, valor)

    db.commit()
    db.refresh(producto_db)

    return producto_db


@router.delete("/{id_producto}")
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):
    producto_db = db.query(Producto).filter(
        Producto.id_producto == id_producto
    ).first()

    if not producto_db:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_db.estado = "inactivo"

    db.commit()

    return {"message": "Producto desactivado correctamente"}