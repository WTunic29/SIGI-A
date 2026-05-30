from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.pedido_detalle import PedidoDetalle
from app.models.pedido import Pedido
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.pedido_detalle import (
    PedidoDetalleCreate,
    PedidoDetalleUpdate,
    PedidoDetalleResponse
)

router = APIRouter(
    prefix="/pedido-detalle",
    tags=["Pedido Detalle"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO PEDIDO
# =========================

def validar_acceso_pedido(
    pedido: Pedido,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if current_user.rol == "cliente":

        if pedido.id_usuario != current_user.id_usuario:
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

        if pedido.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )


# =========================
# CREAR DETALLE
# =========================

@router.post("/", response_model=PedidoDetalleResponse)
def crear_detalle(
    detalle: PedidoDetalleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == detalle.id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    validar_acceso_pedido(
        pedido,
        current_user,
        db
    )

    nuevo = PedidoDetalle(**detalle.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR DETALLES
# =========================

@router.get("/", response_model=list[PedidoDetalleResponse])
def listar_detalles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(PedidoDetalle).all()

    # CLIENTE
    if current_user.rol == "cliente":

        return (
            db.query(PedidoDetalle)
            .join(Pedido)
            .filter(
                Pedido.id_usuario == current_user.id_usuario
            )
            .all()
        )

    # NEGOCIO
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return (
        db.query(PedidoDetalle)
        .join(Pedido)
        .filter(
            Pedido.id_negocio == negocio.id_negocio
        )
        .all()
    )


# =========================
# OBTENER DETALLE
# =========================

@router.get("/{id_detalle}", response_model=PedidoDetalleResponse)
def obtener_detalle(
    id_detalle: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == detalle.id_pedido
    ).first()

    validar_acceso_pedido(
        pedido,
        current_user,
        db
    )

    return detalle


# =========================
# ACTUALIZAR DETALLE
# =========================

@router.put("/{id_detalle}", response_model=PedidoDetalleResponse)
def actualizar_detalle(
    id_detalle: int,
    datos: PedidoDetalleUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == detalle.id_pedido
    ).first()

    validar_acceso_pedido(
        pedido,
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
        require_roles(["negocio", "admin"])
    )
):

    detalle = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido_detalle == id_detalle
    ).first()

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == detalle.id_pedido
    ).first()

    validar_acceso_pedido(
        pedido,
        current_user,
        db
    )

    db.delete(detalle)
    db.commit()

    return {
        "message": "Detalle eliminado"
    }