from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.user import Usuario

from app.schemas.carrito import (
    CarritoCreate,
    CarritoUpdate,
    CarritoResponse
)
from app.schemas.carrito_completo import CarritoActivoResponse
from app.schemas.checkout import CheckoutRequest, CheckoutResponse
from app.services.checkout import ejecutar_checkout
from app.utils.carrito_helpers import (
    calcular_total_carrito,
    enriquecer_detalle_response,
)

router = APIRouter(
    prefix="/carritos",
    tags=["Carritos"]
)


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
# CARRITO ACTIVO DEL CLIENTE
# =========================

@router.get("/activo/me", response_model=CarritoActivoResponse)
def obtener_carrito_activo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    ),
):
    id_usuario = current_user.id_usuario
    if current_user.rol == "admin":
        raise HTTPException(
            status_code=400,
            detail="Use GET /carritos/{id} como administrador",
        )

    carrito = db.query(Carrito).filter(
        Carrito.id_usuario == id_usuario,
        Carrito.estado == "activo",
    ).order_by(Carrito.id_carrito.desc()).first()

    if not carrito:
        carrito = Carrito(
            id_usuario=id_usuario,
            estado="activo",
            fecha_creacion=datetime.utcnow(),
        )
        db.add(carrito)
        db.commit()
        db.refresh(carrito)

    detalles = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito
    ).all()

    detalles_resp = [
        enriquecer_detalle_response(db, det) for det in detalles
    ]

    return CarritoActivoResponse(
        carrito=carrito,
        detalles=detalles_resp,
        total=calcular_total_carrito(detalles),
        cantidad_items=len(detalles),
    )


# =========================
# CHECKOUT
# =========================

@router.post("/{id_carrito}/checkout", response_model=CheckoutResponse)
def checkout_carrito(
    id_carrito: int,
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    ),
):
    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    validar_acceso_carrito(carrito, current_user)

    return ejecutar_checkout(
        db,
        carrito,
        current_user,
        body.metodo_pago,
        body.referencia_externa,
    )


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