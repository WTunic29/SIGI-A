from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.producto import Producto
from app.models.user import Usuario

from app.schemas.carrito import (
    CarritoCreate,
    CarritoUpdate,
    CarritoResponse
)
from app.schemas.carrito_detalle import AgregarProductoCarrito

router = APIRouter(
    prefix="/carritos",
    tags=["Carritos"]
)

from app.utils.auditoria import registrar_auditoria

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO CARRITO
# =========================

def validar_acceso_carrito(
    carrito: Carrito,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if carrito.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

# =========================
# HELPERS CARRITO
# =========================

def obtener_carrito_activo_usuario(
    db: Session,
    id_usuario: int
):
    return db.query(Carrito).filter(
        Carrito.id_usuario == id_usuario,
        Carrito.estado == "activo"
    ).order_by(
        Carrito.id_carrito.desc()
    ).first()


def recalcular_total_carrito(
    db: Session,
    carrito: Carrito
):
    detalles = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    total = sum([
        detalle.subtotal or 0
        for detalle in detalles
    ])

    carrito.total_estimado = total
    carrito.fecha_actualizacion = datetime.utcnow()
    return total

def liberar_reservas_vencidas(db: Session):
    ahora = datetime.utcnow()

    detalles_vencidos = db.query(CarritoDetalle).filter(
        CarritoDetalle.estado_reserva == "RESERVADO",
        CarritoDetalle.fecha_expiracion_reserva < ahora
    ).all()

    carritos_afectados = set()

    for detalle in detalles_vencidos:
        detalle.estado_reserva = "VENCIDO"
        carritos_afectados.add(detalle.id_carrito)

    for id_carrito in carritos_afectados:
        carrito = db.query(Carrito).filter(
            Carrito.id_carrito == id_carrito
        ).first()

        if carrito:
            recalcular_total_carrito(db, carrito)

    return len(detalles_vencidos)

def obtener_stock_disponible_producto(
    db: Session,
    producto: Producto
):
    cantidad_reservada = db.query(
        func.coalesce(func.sum(CarritoDetalle.cantidad), 0)
    ).filter(
        CarritoDetalle.id_producto == producto.id_producto,
        CarritoDetalle.estado_reserva == "RESERVADO",
        CarritoDetalle.fecha_expiracion_reserva > datetime.utcnow()
    ).scalar()

    return producto.stock - cantidad_reservada

# =========================
# OBTENER CARRITO ACTIVO
# =========================

@router.get("/activo", response_model=CarritoResponse | None)
def obtener_carrito_activo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)
    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        return None
    db.flush()
    recalcular_total_carrito(db, carrito)
    db.commit()
    db.refresh(carrito)

    return carrito

# =========================
# OBTENER CARRITO ACTIVO CON DETALLE
# =========================

@router.get("/activo/detalle")
def obtener_carrito_activo_detalle(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)

    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        return {
            "carrito": None,
            "items": []
        }

    recalcular_total_carrito(db, carrito)
    db.commit()
    db.refresh(carrito)

    detalles = db.query(
        CarritoDetalle,
        Producto
    ).join(
        Producto,
        Producto.id_producto == CarritoDetalle.id_producto
    ).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    items = []

    for detalle, producto in detalles:
        items.append({
            "id_carrito_detalle": detalle.id_carrito_detalle,
            "id_carrito": detalle.id_carrito,
            "tipo_item": detalle.tipo_item,
            "id_producto": detalle.id_producto,
            "id_servicio": detalle.id_servicio,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "imagen_url": producto.imagen_url,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal,
            "estado_reserva": detalle.estado_reserva,
            "fecha_reserva": detalle.fecha_reserva,
            "fecha_expiracion_reserva": detalle.fecha_expiracion_reserva
        })

    return {
        "carrito": carrito,
        "items": items
    }

# =========================
# AGREGAR PRODUCTO AL CARRITO
# =========================

@router.post("/agregar-producto", response_model=CarritoResponse)
def agregar_producto_carrito(
    request: Request,
    datos: AgregarProductoCarrito,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):
    liberar_reservas_vencidas(db)
    if datos.cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor a cero"
        )

    producto = db.query(Producto).filter(
        Producto.id_producto == datos.id_producto,
        Producto.estado == "activo"
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o inactivo"
        )

    stock_disponible = obtener_stock_disponible_producto(
        db,
        producto
    )

    if stock_disponible < datos.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible actualmente: {stock_disponible}"
        )  

    ahora = datetime.utcnow()
    expiracion = ahora + timedelta(minutes=15)

    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        carrito = Carrito(
            id_usuario=current_user.id_usuario,
            id_negocio=producto.id_negocio,
            estado="activo",
            fecha_creacion=ahora,
            fecha_expiracion=expiracion,
            fecha_actualizacion=ahora,
            total_estimado=0
        )
        db.add(carrito)
        db.flush()
    else:
        if carrito.id_negocio and carrito.id_negocio != producto.id_negocio:
            raise HTTPException(
                status_code=400,
                detail="No puedes mezclar productos de diferentes negocios en el mismo carrito"
            )

        carrito.id_negocio = producto.id_negocio
        carrito.fecha_expiracion = expiracion
        carrito.fecha_actualizacion = ahora

    subtotal = producto.precio * datos.cantidad

    detalle_existente = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.id_producto == producto.id_producto,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).first()

    if detalle_existente:
        nueva_cantidad = detalle_existente.cantidad + datos.cantidad

        cantidad_actual_en_carrito = detalle_existente.cantidad or 0
        stock_disponible_real = stock_disponible + cantidad_actual_en_carrito

        if stock_disponible_real < nueva_cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para aumentar la cantidad. Disponible actualmente: {stock_disponible_real}"
            )

        detalle_existente.cantidad = nueva_cantidad
        detalle_existente.precio_unitario = producto.precio
        detalle_existente.subtotal = producto.precio * nueva_cantidad
        detalle_existente.fecha_reserva = ahora
        detalle_existente.fecha_expiracion_reserva = expiracion
    else:
        detalle = CarritoDetalle(
            id_carrito=carrito.id_carrito,
            tipo_item="producto",
            id_producto=producto.id_producto,
            id_servicio=None,
            cantidad=datos.cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal,
            estado_reserva="RESERVADO",
            fecha_reserva=ahora,
            fecha_expiracion_reserva=expiracion
        )
        db.add(detalle)
    db.flush()
    recalcular_total_carrito(db, carrito)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="ITEM_AGREGADO_CARRITO",
        modulo="carritos",
        tabla_afectada="core.carrito_detalle",
        id_registro=carrito.id_carrito,
        detalle=(
            f"Usuario {current_user.correo} agregó producto ID "
            f"{producto.id_producto} al carrito por cantidad {datos.cantidad}. "
            f"Reserva válida hasta {expiracion}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    db.commit()
    db.refresh(carrito)

    return carrito

# =========================
# CONVERTIR CARRITO A PEDIDO
# =========================

@router.post("/{id_carrito}/convertir")
def convertir_carrito_a_pedido(
    id_carrito: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    if carrito.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="El carrito ya no está activo"
        )

    detalles_reservados = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    if not detalles_reservados:
        raise HTTPException(
            status_code=400,
            detail="El carrito no tiene reservas activas"
        )

    for detalle in detalles_reservados:
        detalle.estado_reserva = "CONVERTIDO"

    carrito.estado = "cerrado"
    carrito.fecha_actualizacion = datetime.utcnow()

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CARRITO_CONVERTIDO_PEDIDO",
        modulo="carritos",
        tabla_afectada="core.carritos",
        id_registro=carrito.id_carrito,
        detalle=(
            f"Usuario {current_user.correo} convirtió el carrito "
            f"ID {carrito.id_carrito} en pedido."
        ),
        nivel="INFO",
        resultado="OK"
    )

    db.commit()
    db.refresh(carrito)

    return {
        "message": "Carrito cerrado correctamente después de crear el pedido",
        "id_carrito": carrito.id_carrito,
        "estado": carrito.estado
    }

# =========================
# CREAR CARRITO
# =========================

@router.post("/", response_model=CarritoResponse)
def crear_carrito(
    carrito: CarritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):

    nuevo = Carrito(
        id_usuario=current_user.id_usuario,
        estado=carrito.estado,
        fecha_creacion=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR CARRITOS
# =========================

@router.get("/", response_model=list[CarritoResponse])
def listar_carritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Carrito).all()

    # CLIENTE
    return db.query(Carrito).filter(
        Carrito.id_usuario == current_user.id_usuario
    ).all()


# =========================
# OBTENER CARRITO
# =========================

@router.get("/{id_carrito}", response_model=CarritoResponse)
def obtener_carrito(
    id_carrito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    return carrito


# =========================
# ACTUALIZAR CARRITO
# =========================

@router.put("/{id_carrito}", response_model=CarritoResponse)
def actualizar_carrito(
    id_carrito: int,
    datos: CarritoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(carrito, key, value)

    db.commit()
    db.refresh(carrito)

    return carrito


# =========================
# ELIMINAR CARRITO
# =========================

@router.delete("/{id_carrito}")
def eliminar_carrito(
    id_carrito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    db.delete(carrito)
    db.commit()

    return {
        "message": "Carrito eliminado"
    }
