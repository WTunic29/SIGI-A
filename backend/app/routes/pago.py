from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import SessionLocal
from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.pedido_detalle import PedidoDetalle
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.models.factura import Factura
from app.models.producto import Producto
from app.models.cita import Cita

from app.schemas.pago import (
    PagoCreate,
    PagoUpdate,
    PagoResponse
)

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)

from app.routes.factura import (
    generar_numero_factura,
    generar_pdf_factura_archivo
)

from app.utils.email import enviar_email_con_adjunto

# =========================
# DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO PAGO
# =========================

def validar_acceso_pago(
    pago: Pago,
    current_user: Usuario,
    db: Session
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if current_user.rol == "cliente":

        pedido = db.query(Pedido).filter(
            Pedido.id_pedido == pago.id_pedido
        ).first()

        if not pedido or pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    # NEGOCIO
    elif current_user.rol == "negocio":

        pedido = db.query(Pedido).filter(
            Pedido.id_pedido == pago.id_pedido
        ).first()

        negocio = None
        if pedido:
            negocio = db.query(Negocio).filter(
                Negocio.id_negocio == pedido.id_negocio,
                Negocio.id_usuario_propietario == current_user.id_usuario
            ).first()

        if not pedido or not negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para este negocio"
            )


# =========================
# CREAR PAGO
# =========================

@router.post("/", response_model=PagoResponse)
def crear_pago(
    pago: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio"])
    )
):

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == pago.id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    # CLIENTE SOLO SUS PEDIDOS
    if current_user.rol == "cliente":

        if pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )

    # NEGOCIO SOLO SUS PEDIDOS
    elif current_user.rol == "negocio":

        negocio = db.query(Negocio).filter(
            Negocio.id_negocio == pedido.id_negocio,
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para este negocio"
            )
    if pago.estado_pago == "aprobado" and pedido.estado == "pagado":
        raise HTTPException(
            status_code=400,
            detail="Este pedido ya fue pagado"
        )

    nuevo_pago = Pago(
        id_pedido=pago.id_pedido,
        metodo_pago=pago.metodo_pago,
        referencia_externa=pago.referencia_externa,
        estado_pago=pago.estado_pago,
        valor=pago.valor,
        fecha_pago=datetime.utcnow(),
        respuesta_pasarela=pago.respuesta_pasarela
    )

    db.add(nuevo_pago)

    if pago.estado_pago == "aprobado":
        pedido.estado = "pagado"

        detalles_pedido = db.query(PedidoDetalle).filter(
            PedidoDetalle.id_pedido == pedido.id_pedido
        ).all()

        for detalle in detalles_pedido:
            if detalle.tipo_item == "producto" and detalle.id_producto:
                producto = db.query(Producto).filter(
                    Producto.id_producto == detalle.id_producto
                ).first()

                if not producto:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto ID {detalle.id_producto} no encontrado"
                    )

                if producto.stock < detalle.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para el producto {producto.nombre}"
                    )

                producto.stock = producto.stock - detalle.cantidad

            if detalle.id_cita:
                cita = db.query(Cita).filter(
                    Cita.id_cita == detalle.id_cita
                ).first()

                if cita and cita.estado in ["pendiente_pago", "reservada_carrito"]:
                    cita.estado = "confirmada"

        factura = db.query(Factura).filter(
            Factura.id_pedido == pedido.id_pedido
        ).first()

        if not factura and detalles_pedido:
            subtotal = sum([
                detalle.subtotal or 0
                for detalle in detalles_pedido
            ])

            cliente = db.query(Usuario).filter(
                Usuario.id_usuario == pedido.id_usuario
            ).first()

            correo_destino = pago.correo_factura

            if not correo_destino and cliente:
                correo_destino = cliente.correo

            factura = Factura(
                numero_factura=generar_numero_factura(pedido.id_pedido),
                id_pedido=pedido.id_pedido,
                id_usuario=pedido.id_usuario,
                id_negocio=pedido.id_negocio,
                subtotal=subtotal,
                impuestos=0,
                total=pedido.total,
                estado="emitida",
                correo_destino=correo_destino
            )

            db.add(factura)
            db.flush()
            db.refresh(factura)

        if factura:
            try:
                ruta_pdf = factura.ruta_pdf

                if not ruta_pdf:
                    ruta_pdf = generar_pdf_factura_archivo(
                        db,
                        factura
                    )

                if factura.correo_destino:
                    enviar_email_con_adjunto(
                        destino=factura.correo_destino,
                        asunto=f"Factura {factura.numero_factura} - SIGI-A",
                        cuerpo=(
                            "Hola,\n\n"
                            "Adjuntamos tu factura generada en SIGI-A.\n\n"
                            f"Número de factura: {factura.numero_factura}\n"
                            f"Total: ${float(factura.total):,.0f}\n\n"
                            "Gracias por usar SIGI-A."
                        ),
                        ruta_adjunto=ruta_pdf,
                        nombre_adjunto=factura.nombre_archivo_pdf or f"{factura.numero_factura}.pdf"
                    )

                    factura.estado = "enviada"
                    factura.fecha_envio_correo = datetime.utcnow()

            except Exception as error_email:
                mensaje_actual = nuevo_pago.respuesta_pasarela or ""
                nuevo_pago.respuesta_pasarela = (
                    f"{mensaje_actual} | Factura generada, pero no se pudo enviar por correo: {str(error_email)}"
                )

    db.commit()
    db.refresh(nuevo_pago)

    return nuevo_pago

# =========================
# LISTAR PAGOS
# =========================

@router.get("/", response_model=list[PagoResponse])
def listar_pagos(
    id_negocio: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        query = db.query(Pago).join(Pedido, Pedido.id_pedido == Pago.id_pedido)
        if id_negocio:
            query = query.filter(Pedido.id_negocio == id_negocio)
        return query.all()

    # CLIENTE
    if current_user.rol == "cliente":

        pagos = (
            db.query(Pago)
            .join(Pedido, Pedido.id_pedido == Pago.id_pedido)
            .filter(
                Pedido.id_usuario == current_user.id_usuario
            )
            .all()
        )

        return pagos

    # NEGOCIO
    negocios_propios = db.query(Negocio.id_negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).all()

    ids_negocios = [n.id_negocio for n in negocios_propios]

    if not ids_negocios:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    query = db.query(Pago).join(Pedido, Pedido.id_pedido == Pago.id_pedido)

    if id_negocio:
        if id_negocio not in ids_negocios:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para consultar este negocio"
            )
        query = query.filter(Pedido.id_negocio == id_negocio)
    else:
        query = query.filter(Pedido.id_negocio.in_(ids_negocios))

    return query.all()


# =========================
# OBTENER PAGO
# =========================

@router.get("/{id_pago}", response_model=PagoResponse)
def obtener_pago(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    validar_acceso_pago(
        pago,
        current_user,
        db
    )

    return pago


# =========================
# ACTUALIZAR PAGO
# =========================

@router.put("/{id_pago}", response_model=PagoResponse)
def actualizar_pago(
    id_pago: int,
    datos: PagoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin"])
    )
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    validar_acceso_pago(
        pago,
        current_user,
        db
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(pago, key, value)

    db.commit()
    db.refresh(pago)

    return pago


# =========================
# ELIMINAR PAGO
# =========================

@router.delete("/{id_pago}")
def eliminar_pago(
    id_pago: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    pago = db.query(Pago).filter(
        Pago.id_pago == id_pago
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    db.delete(pago)
    db.commit()

    return {
        "message": "Pago eliminado correctamente"
    }
