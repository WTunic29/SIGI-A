from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.carrito_detalle import CarritoDetalle
from app.models.carrito import Carrito
from app.models.user import Usuario

from app.schemas.carrito_detalle import (
    CarritoDetalleCreate,
    CarritoDetalleUpdate,
    CarritoDetalleResponse
)
from app.utils.carrito_helpers import (
    validar_y_normalizar_detalle,
    enriquecer_detalle_response,
)

router = APIRouter(
    prefix="/carrito-detalle",
    tags=["Carrito Detalle"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO DETALLE
# =========================

def validar_acceso_detalle(
    detalle: CarritoDetalle,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == detalle.id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    if carrito.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )


# =========================
# CREAR DETALLE
# =========================

@router.post("/", response_model=CarritoDetalleResponse)
def crear_detalle(
    detalle: CarritoDetalleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == detalle.id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    if current_user.rol != "admin":

        if carrito.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    nuevo = CarritoDetalle(**validar_y_normalizar_detalle(db, detalle))

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return enriquecer_detalle_response(db, nuevo)


# =========================
# LISTAR DETALLES
# =========================

@router.get("/", response_model=list[CarritoDetalleResponse])
def listar_detalles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(CarritoDetalle).all()

    detalles = (
        db.query(CarritoDetalle)
        .join(
            Carrito,
            Carrito.id_carrito == CarritoDetalle.id_carrito
        )
        .filter(
            Carrito.id_usuario == current_user.id_usuario
        )
        .all()
    )

    return detalles


# =========================
# OBTENER DETALLE
# =========================

@router.get("/{id_detalle}", response_model=CarritoDetalleResponse)
def obtener_detalle(
    id_detalle: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    validar_acceso_detalle(
        detalle,
        current_user,
        db
    )

    return detalle


# =========================
# ACTUALIZAR DETALLE
# =========================

@router.put("/{id_detalle}", response_model=CarritoDetalleResponse)
def actualizar_detalle(
    id_detalle: int,
    datos: CarritoDetalleUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    validar_acceso_detalle(
        detalle,
        current_user,
        db
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(detalle, key, value)

    db.commit()
    db.refresh(detalle)

    return detalle


# =========================
# ELIMINAR DETALLE
# =========================

@router.delete("/{id_detalle}")
def eliminar_detalle(
    id_detalle: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    detalle = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    validar_acceso_detalle(
        detalle,
        current_user,
        db
    )

    db.delete(detalle)
    db.commit()

    return {
        "message": "Detalle eliminado"
    }