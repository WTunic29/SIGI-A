from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.pedido import Pedido
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.pedido import (
    PedidoCreate,
    PedidoUpdate,
    PedidoResponse
)

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
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
            Negocio.id_usuario_propietario == current_user.id_usuario
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
# CREAR PEDIDO
# =========================

@router.post("/", response_model=PedidoResponse)
def crear_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):

    nuevo_pedido = Pedido(
        id_usuario=current_user.id_usuario,
        id_negocio=pedido.id_negocio,
        total=pedido.total,
        estado=pedido.estado,
        fecha=datetime.utcnow()
    )

    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)

    return nuevo_pedido


# =========================
# LISTAR PEDIDOS
# =========================

@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Pedido).all()

    # CLIENTE
    if current_user.rol == "cliente":

        return db.query(Pedido).filter(
            Pedido.id_usuario == current_user.id_usuario
        ).all()

    # NEGOCIO
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return db.query(Pedido).filter(
        Pedido.id_negocio == negocio.id_negocio
    ).all()


# =========================
# OBTENER PEDIDO
# =========================

@router.get("/{id_pedido}", response_model=PedidoResponse)
def obtener_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
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

    return pedido


# =========================
# ACTUALIZAR PEDIDO
# =========================

@router.put("/{id_pedido}", response_model=PedidoResponse)
def actualizar_pedido(
    id_pedido: int,
    datos: PedidoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
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

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(pedido, key, value)

    db.commit()
    db.refresh(pedido)

    return pedido


# =========================
# ELIMINAR PEDIDO
# =========================

@router.delete("/{id_pedido}")
def eliminar_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    db.delete(pedido)
    db.commit()

    return {
        "message": "Pedido eliminado"
    }