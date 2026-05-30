from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.deps import require_roles
from app.models.user import Usuario
from app.models.factura import Factura
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.negocio import Negocio
from app.services.checkout import _construir_factura_response
from app.schemas.factura import FacturaResponse

router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _validar_acceso_factura(
    factura: Factura,
    current_user: Usuario,
    db: Session,
):
    if current_user.rol == "admin":
        return

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == factura.id_pedido
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if current_user.rol == "cliente":
        if pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(status_code=403, detail="No autorizado")
        return

    if current_user.rol == "negocio":
        negocio = db.query(Negocio).filter(
            Negocio.id_usuario == current_user.id_usuario
        ).first()
        if not negocio or pedido.id_negocio != negocio.id_negocio:
            raise HTTPException(status_code=403, detail="No autorizado")


@router.get("/{id_factura}", response_model=FacturaResponse)
def obtener_factura(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    ),
):
    factura = db.query(Factura).filter(
        Factura.id_factura == id_factura
    ).first()

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    _validar_acceso_factura(factura, current_user, db)

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == factura.id_pedido
    ).first()
    pago = db.query(Pago).filter(Pago.id_pago == factura.id_pago).first()

    if not pedido or not pago:
        raise HTTPException(status_code=404, detail="Datos de factura incompletos")

    return _construir_factura_response(db, factura, pedido, pago)


@router.get("/pedido/{id_pedido}", response_model=FacturaResponse)
def obtener_factura_por_pedido(
    id_pedido: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    ),
):
    factura = db.query(Factura).filter(
        Factura.id_pedido == id_pedido
    ).first()

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    _validar_acceso_factura(factura, current_user, db)

    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    pago = db.query(Pago).filter(Pago.id_pago == factura.id_pago).first()

    if not pedido or not pago:
        raise HTTPException(status_code=404, detail="Datos de factura incompletos")

    return _construir_factura_response(db, factura, pedido, pago)
