from fastapi import APIRouter, Depends, HTTPException, Request
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

from app.utils.auditoria import registrar_auditoria

router = APIRouter()


# =========================
# VALIDAR ACCESO PRODUCTO
# =========================

def validar_acceso_producto(
    producto: Producto,
    current_user: Usuario,
    db: Session
):
    # ADMIN puede gestionar cualquier producto
    if current_user.rol == "admin":
        return

    # NEGOCIO solo puede gestionar productos de su propio negocio
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
            detail="No autorizado para gestionar este producto"
        )


# =========================
# CREAR PRODUCTO
# =========================

@router.post("/", response_model=ProductoResponse)
def crear_producto(
    request: Request,
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):
    # NEGOCIO: se asigna automáticamente a su negocio
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

    # ADMIN: puede crear producto para cualquier negocio
    else:
        if not producto.id_negocio:
            raise HTTPException(
                status_code=400,
                detail="El administrador debe enviar id_negocio"
            )

        negocio = db.query(Negocio).filter(
            Negocio.id_negocio == producto.id_negocio
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

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

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="PRODUCTO_CREADO",
        modulo="productos",
        tabla_afectada="core.productos",
        id_registro=nuevo_producto.id_producto,
        detalle=(
            f"Usuario {current_user.correo} creó el producto "
            f"{nuevo_producto.nombre} para el negocio ID {nuevo_producto.id_negocio}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    return nuevo_producto


# =========================
# LISTAR PRODUCTOS PÚBLICOS PARA TIENDA
# =========================

@router.get("/publicos", response_model=List[ProductoResponse])
def listar_productos_publicos(
    db: Session = Depends(get_db)
):
    return db.query(Producto).filter(
        Producto.estado == "activo"
    ).all()


# =========================
# LISTAR PRODUCTOS SEGÚN ROL
# =========================

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin", "superadmin"])
    )
):
    # ADMIN / SUPERADMIN ven todos
    if current_user.rol in ["admin", "superadmin"]:
        return db.query(Producto).all()

    # NEGOCIO ve solo sus productos
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

    # CLIENTE ve productos activos
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

    if producto.estado != "activo":
        raise HTTPException(
            status_code=404,
            detail="Producto no disponible"
        )

    return producto


# =========================
# ACTUALIZAR PRODUCTO
# =========================

@router.put("/{id_producto}", response_model=ProductoResponse)
def actualizar_producto(
    request: Request,
    id_producto: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin", "superadmin"])
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

    if not datos:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar"
        )

    cambios = []

    for campo, valor in datos.items():
        valor_anterior = getattr(producto_db, campo, None)

        if valor_anterior != valor:
            cambios.append(f"{campo}: {valor_anterior} -> {valor}")

        setattr(producto_db, campo, valor)

    db.commit()
    db.refresh(producto_db)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="PRODUCTO_ACTUALIZADO",
        modulo="productos",
        tabla_afectada="core.productos",
        id_registro=producto_db.id_producto,
        detalle=(
            f"Usuario {current_user.correo} actualizó el producto "
            f"{producto_db.nombre}. Cambios: {', '.join(cambios) if cambios else 'Sin cambios detectados'}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    return producto_db


# =========================
# ELIMINAR / DESACTIVAR PRODUCTO
# =========================

@router.delete("/{id_producto}")
def eliminar_producto(
    request: Request,
    id_producto: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin", "superadmin"])
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

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="PRODUCTO_ELIMINADO",
        modulo="productos",
        tabla_afectada="core.productos",
        id_registro=producto_db.id_producto,
        detalle=(
            f"Usuario {current_user.correo} desactivó/eliminó lógicamente "
            f"el producto {producto_db.nombre}."
        ),
        nivel="WARNING",
        resultado="OK"
    )

    return {
        "message": "Producto desactivado correctamente"
    }