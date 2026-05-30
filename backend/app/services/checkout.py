"""Checkout atómico: carrito → pedido(s) + citas + pago + factura."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita
from app.models.empleado import Empleado
from app.models.factura import Factura
from app.models.negocio import Negocio
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.pedido_detalle import PedidoDetalle
from app.models.producto import Producto
from app.models.servicio import Servicio
from app.models.user import Usuario
from app.routes.cita import validar_disponibilidad_cita
from app.schemas.checkout import CheckoutResponse
from app.schemas.factura import FacturaLineaResponse, FacturaResponse
from app.schemas.pago import PagoResponse
from app.schemas.pedido import PedidoResponse


def _generar_numero_factura(db: Session) -> str:
    year = datetime.utcnow().year
    prefijo = f"FAC-{year}-"
    ultima = (
        db.query(Factura)
        .filter(Factura.numero_factura.like(f"{prefijo}%"))
        .order_by(Factura.id_factura.desc())
        .first()
    )
    if ultima and ultima.numero_factura.startswith(prefijo):
        try:
            secuencia = int(ultima.numero_factura.split("-")[-1]) + 1
        except ValueError:
            secuencia = 1
    else:
        secuencia = 1
    return f"{prefijo}{secuencia:06d}"


def _resolver_id_negocio_item(db: Session, item: CarritoDetalle) -> int:
    if item.id_negocio:
        return int(item.id_negocio)
    if item.tipo_item == "producto" and item.id_producto:
        producto = db.query(Producto).filter(
            Producto.id_producto == item.id_producto
        ).first()
        if producto:
            return int(producto.id_negocio)
    if item.tipo_item == "servicio" and item.id_servicio:
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == item.id_servicio
        ).first()
        if servicio:
            return int(servicio.id_negocio)
    raise HTTPException(
        status_code=400,
        detail="Cada ítem del carrito debe incluir id_negocio o referencia válida",
    )


def _construir_factura_response(
    db: Session,
    factura: Factura,
    pedido: Pedido,
    pago: Pago,
) -> FacturaResponse:
    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == pedido.id_negocio
    ).first()
    lineas: List[FacturaLineaResponse] = []
    detalles = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido == pedido.id_pedido
    ).all()

    for det in detalles:
        descripcion = "Ítem"
        fecha_cita = None
        hora_inicio = None

        if det.tipo_item == "producto" and det.id_producto:
            producto = db.query(Producto).filter(
                Producto.id_producto == det.id_producto
            ).first()
            descripcion = producto.nombre if producto else f"Producto #{det.id_producto}"
        elif det.tipo_item == "servicio" and det.id_servicio:
            servicio = db.query(Servicio).filter(
                Servicio.id_servicio == det.id_servicio
            ).first()
            descripcion = servicio.nombre if servicio else f"Servicio #{det.id_servicio}"
            if det.id_cita:
                cita = db.query(Cita).filter(Cita.id_cita == det.id_cita).first()
                if cita:
                    fecha_cita = str(cita.fecha)
                    hora_inicio = str(cita.hora_inicio)

        lineas.append(
            FacturaLineaResponse(
                tipo_item=det.tipo_item,
                descripcion=descripcion,
                cantidad=det.cantidad,
                precio_unitario=det.precio_unitario,
                subtotal=det.subtotal,
                id_cita=det.id_cita,
                fecha_cita=fecha_cita,
                hora_inicio=hora_inicio,
            )
        )

    return FacturaResponse(
        id_factura=factura.id_factura,
        id_pedido=factura.id_pedido,
        id_pago=factura.id_pago,
        numero_factura=factura.numero_factura,
        subtotal=factura.subtotal,
        total=factura.total,
        estado=factura.estado,
        fecha_emision=factura.fecha_emision,
        id_negocio=pedido.id_negocio,
        nombre_negocio=negocio.nombre_negocio if negocio else None,
        metodo_pago=pago.metodo_pago,
        referencia_externa=pago.referencia_externa,
        lineas=lineas,
    )


def ejecutar_checkout(
    db: Session,
    carrito: Carrito,
    usuario: Usuario,
    metodo_pago: str,
    referencia_externa: str | None,
) -> CheckoutResponse:
    if carrito.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="El carrito no está activo",
        )

    detalles = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito
    ).all()

    if not detalles:
        raise HTTPException(
            status_code=400,
            detail="El carrito está vacío",
        )

    por_negocio: dict[int, list[CarritoDetalle]] = defaultdict(list)
    for item in detalles:
        id_negocio = _resolver_id_negocio_item(db, item)
        por_negocio[id_negocio].append(item)

    pedidos_resp: List[PedidoResponse] = []
    pagos_resp: List[PagoResponse] = []
    facturas_resp: List[FacturaResponse] = []
    resumen = []

    try:
        for id_negocio, items in por_negocio.items():
            total_pedido = Decimal("0")
            lineas_pedido: List[Tuple[CarritoDetalle, Decimal, int | None]] = []

            for item in items:
                subtotal = Decimal(str(item.precio_unitario)) * int(item.cantidad)

                if item.tipo_item == "producto":
                    producto = db.query(Producto).filter(
                        Producto.id_producto == item.id_producto,
                        Producto.estado == "activo",
                    ).first()
                    if not producto:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Producto {item.id_producto} no disponible",
                        )
                    if int(producto.stock or 0) < int(item.cantidad):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Stock insuficiente para {producto.nombre}",
                        )
                    lineas_pedido.append((item, subtotal, None))

                elif item.tipo_item == "servicio":
                    if not all([
                        item.id_servicio,
                        item.id_empleado,
                        item.fecha_cita,
                        item.hora_inicio,
                    ]):
                        raise HTTPException(
                            status_code=400,
                            detail="Los servicios agendados requieren empleado, fecha y hora",
                        )
                    servicio, hora_fin = validar_disponibilidad_cita(
                        db,
                        int(item.id_empleado),
                        int(item.id_servicio),
                        id_negocio,
                        item.fecha_cita,
                        item.hora_inicio,
                        hora_fin=item.hora_fin,
                    )
                    item.hora_fin = hora_fin
                    lineas_pedido.append((item, subtotal, None))
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"tipo_item no soportado: {item.tipo_item}",
                    )

                total_pedido += subtotal

            pedido = Pedido(
                id_usuario=usuario.id_usuario,
                id_negocio=id_negocio,
                total=total_pedido,
                estado="pendiente",
                fecha=datetime.utcnow(),
            )
            db.add(pedido)
            db.flush()

            for item, subtotal, _ in lineas_pedido:
                id_cita = None

                if item.tipo_item == "servicio":
                    cita = Cita(
                        id_cliente=usuario.id_usuario,
                        id_negocio=id_negocio,
                        id_empleado=int(item.id_empleado),
                        fecha=item.fecha_cita,
                        hora_inicio=item.hora_inicio,
                        hora_fin=item.hora_fin,
                        estado="confirmada",
                        observaciones=item.observaciones,
                    )
                    db.add(cita)
                    db.flush()

                    servicio = db.query(Servicio).filter(
                        Servicio.id_servicio == item.id_servicio
                    ).first()
                    db.add(
                        DetalleCita(
                            id_cita=cita.id_cita,
                            id_servicio=int(item.id_servicio),
                            precio=item.precio_unitario,
                            duracion=servicio.duracion_minutos if servicio else 30,
                        )
                    )
                    id_cita = cita.id_cita

                elif item.tipo_item == "producto":
                    producto = db.query(Producto).filter(
                        Producto.id_producto == item.id_producto
                    ).first()
                    if producto:
                        producto.stock = int(producto.stock or 0) - int(item.cantidad)

                db.add(
                    PedidoDetalle(
                        id_pedido=pedido.id_pedido,
                        tipo_item=item.tipo_item,
                        id_producto=item.id_producto,
                        id_servicio=item.id_servicio,
                        id_cita=id_cita,
                        cantidad=item.cantidad,
                        precio_unitario=item.precio_unitario,
                        subtotal=subtotal,
                    )
                )

            pedido.estado = "pagado"
            db.flush()

            referencia = referencia_externa or f"CHK-{pedido.id_pedido}-{int(datetime.utcnow().timestamp())}"
            pago = Pago(
                id_pedido=pedido.id_pedido,
                metodo_pago=metodo_pago,
                referencia_externa=referencia,
                estado_pago="aprobado",
                valor=total_pedido,
                fecha_pago=datetime.utcnow(),
                respuesta_pasarela="Checkout carrito SIGI-A",
            )
            db.add(pago)
            db.flush()

            factura = Factura(
                id_pedido=pedido.id_pedido,
                id_pago=pago.id_pago,
                numero_factura=_generar_numero_factura(db),
                subtotal=total_pedido,
                total=total_pedido,
                estado="emitida",
            )
            db.add(factura)
            db.flush()

            pedidos_resp.append(PedidoResponse.model_validate(pedido))
            pagos_resp.append(PagoResponse.model_validate(pago))
            facturas_resp.append(
                _construir_factura_response(db, factura, pedido, pago)
            )
            resumen.append({
                "id_pedido": pedido.id_pedido,
                "id_negocio": id_negocio,
                "total": total_pedido,
                "id_pago": pago.id_pago,
                "id_factura": factura.id_factura,
                "numero_factura": factura.numero_factura,
            })

        carrito.estado = "cerrado"
        db.commit()

        from app.schemas.checkout import CheckoutResultItem

        return CheckoutResponse(
            message="Checkout completado",
            id_carrito=carrito.id_carrito,
            pedidos=pedidos_resp,
            pagos=pagos_resp,
            facturas=facturas_resp,
            resumen=[CheckoutResultItem.model_validate(r) for r in resumen],
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error en checkout: {exc}",
        ) from exc
