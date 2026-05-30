"""Utilidades compartidas para carrito y detalle."""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.carrito_detalle import CarritoDetalle
from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.models.producto import Producto
from app.models.servicio import Servicio
from app.routes.cita import validar_disponibilidad_cita
from app.schemas.carrito_detalle import CarritoDetalleCreate, CarritoDetalleResponse


def validar_y_normalizar_detalle(
    db: Session,
    detalle: CarritoDetalleCreate,
) -> dict:
    data = detalle.model_dump()

    if detalle.tipo_item == "producto":
        if not detalle.id_producto:
            raise HTTPException(status_code=400, detail="id_producto es obligatorio")
        producto = db.query(Producto).filter(
            Producto.id_producto == detalle.id_producto,
            Producto.estado == "activo",
        ).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        if int(detalle.cantidad) < 1:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        if int(producto.stock or 0) < int(detalle.cantidad):
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        data["id_negocio"] = detalle.id_negocio or producto.id_negocio
        data["id_servicio"] = None
        data["id_empleado"] = None
        data["fecha_cita"] = None
        data["hora_inicio"] = None
        data["hora_fin"] = None
        data["precio_unitario"] = producto.precio

    elif detalle.tipo_item == "servicio":
        if not detalle.id_servicio:
            raise HTTPException(status_code=400, detail="id_servicio es obligatorio")
        if not all([detalle.id_empleado, detalle.fecha_cita, detalle.hora_inicio]):
            raise HTTPException(
                status_code=400,
                detail="Servicio agendado requiere id_empleado, fecha_cita y hora_inicio",
            )
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == detalle.id_servicio,
            Servicio.estado == "activo",
        ).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        id_negocio = detalle.id_negocio or servicio.id_negocio
        _, hora_fin = validar_disponibilidad_cita(
            db,
            int(detalle.id_empleado),
            int(detalle.id_servicio),
            int(id_negocio),
            detalle.fecha_cita,
            detalle.hora_inicio,
            hora_fin=detalle.hora_fin,
        )
        data["id_negocio"] = id_negocio
        data["id_producto"] = None
        data["cantidad"] = 1
        data["hora_fin"] = hora_fin
        data["precio_unitario"] = servicio.precio
    else:
        raise HTTPException(status_code=400, detail="tipo_item no válido")

    return data


def enriquecer_detalle_response(
    db: Session,
    detalle: CarritoDetalle,
) -> CarritoDetalleResponse:
    nombre_item: Optional[str] = None
    nombre_negocio: Optional[str] = None
    nombre_empleado: Optional[str] = None

    if detalle.tipo_item == "producto" and detalle.id_producto:
        producto = db.query(Producto).filter(
            Producto.id_producto == detalle.id_producto
        ).first()
        if producto:
            nombre_item = producto.nombre
    elif detalle.tipo_item == "servicio" and detalle.id_servicio:
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == detalle.id_servicio
        ).first()
        if servicio:
            nombre_item = servicio.nombre

    if detalle.id_negocio:
        negocio = db.query(Negocio).filter(
            Negocio.id_negocio == detalle.id_negocio
        ).first()
        if negocio:
            nombre_negocio = negocio.nombre_negocio

    if detalle.id_empleado:
        empleado = db.query(Empleado).filter(
            Empleado.id_empleado == detalle.id_empleado
        ).first()
        if empleado:
            nombre_empleado = f"{empleado.nombre} {empleado.apellido}".strip()

    base = CarritoDetalleResponse.model_validate(detalle)
    return base.model_copy(update={
        "nombre_item": nombre_item,
        "nombre_negocio": nombre_negocio,
        "nombre_empleado": nombre_empleado,
    })


def calcular_total_carrito(detalles: list[CarritoDetalle]) -> float:
    total = Decimal("0")
    for det in detalles:
        total += Decimal(str(det.precio_unitario)) * int(det.cantidad)
    return float(total)
