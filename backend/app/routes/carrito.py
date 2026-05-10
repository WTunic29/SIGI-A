from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.carrito import Carrito
from app.models.user import Usuario

from app.schemas.carrito import (
    CarritoCreate,
    CarritoUpdate,
    CarritoResponse
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