
import os
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from app.utils.email import enviar_email_con_adjunto

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)
from app.models.producto import Producto
from app.models.servicio import Servicio
from app.models.factura import Factura
from app.models.pedido import Pedido
from app.models.pedido_detalle import PedidoDetalle
from app.models.pago import Pago
from app.models.user import Usuario
from app.models.negocio import Negocio

from app.schemas.factura import (
    FacturaCreate,
    FacturaResponse
)

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


def generar_numero_factura(id_pedido: int) -> str:
    return f"FAC-SIGI-{id_pedido:06d}"


def validar_acceso_factura(
    factura: Factura,
    current_user: Usuario
):
    if current_user.rol in ["admin", "superadmin"]:
        return

    if factura.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para consultar esta factura"
        )

FACTURAS_DIR = "/app/generated/facturas"


def asegurar_directorio_facturas():
    os.makedirs(FACTURAS_DIR, exist_ok=True)


def obtener_nombre_item(
    db: Session,
    detalle: PedidoDetalle
):
    if detalle.tipo_item == "producto" and detalle.id_producto:
        producto = db.query(Producto).filter(
            Producto.id_producto == detalle.id_producto
        ).first()

        if producto:
            return producto.nombre

    if detalle.tipo_item == "servicio" and detalle.id_servicio:
        servicio = db.query(Servicio).filter(
            Servicio.id_servicio == detalle.id_servicio
        ).first()

        if servicio:
            return servicio.nombre

    return "Item"


def generar_pdf_factura_archivo(
    db: Session,
    factura: Factura
):
    asegurar_directorio_facturas()

    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == factura.id_pedido
    ).first()

    cliente = db.query(Usuario).filter(
        Usuario.id_usuario == factura.id_usuario
    ).first()

    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == factura.id_negocio
    ).first()

    detalles = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido == factura.id_pedido
    ).all()

    nombre_archivo = f"{factura.numero_factura}.pdf"
    ruta_pdf = os.path.join(FACTURAS_DIR, nombre_archivo)

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter

    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "SIGI-A")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y - 14, "Factura interna / comprobante de compra")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 2 * cm, y, factura.numero_factura)

    y -= 2.2 * cm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Datos del negocio")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Negocio: {negocio.nombre_negocio if negocio else 'N/A'}")
    y -= 13
    c.drawString(2 * cm, y, f"Correo: {negocio.email_negocio if negocio and negocio.email_negocio else 'N/A'}")
    y -= 13
    c.drawString(2 * cm, y, f"Teléfono: {negocio.telefono if negocio and negocio.telefono else 'N/A'}")

    y -= 25

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Datos del cliente")
    y -= 14
    c.setFont("Helvetica", 10)
    nombre_cliente = f"{cliente.nombre} {cliente.apellido}" if cliente else "N/A"
    c.drawString(2 * cm, y, f"Cliente: {nombre_cliente}")
    y -= 13
    c.drawString(2 * cm, y, f"Correo: {cliente.correo if cliente else 'N/A'}")
    y -= 13
    c.drawString(2 * cm, y, f"Pedido: #{factura.id_pedido}")
    y -= 13
    c.drawString(2 * cm, y, f"Fecha emisión: {factura.fecha_emision}")

    y -= 30

    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Descripción")
    c.drawRightString(12 * cm, y, "Cant.")
    c.drawRightString(15 * cm, y, "Precio")
    c.drawRightString(width - 2 * cm, y, "Subtotal")
    y -= 10
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 15

    c.setFont("Helvetica", 10)

    for detalle in detalles:
        nombre_item = obtener_nombre_item(db, detalle)

        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 10)

        c.drawString(2 * cm, y, str(nombre_item)[:45])
        c.drawRightString(12 * cm, y, str(detalle.cantidad))
        c.drawRightString(15 * cm, y, f"${float(detalle.precio_unitario):,.0f}")
        c.drawRightString(width - 2 * cm, y, f"${float(detalle.subtotal):,.0f}")
        y -= 16

    y -= 10
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 18

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 2 * cm, y, f"Subtotal: ${float(factura.subtotal):,.0f}")
    y -= 16
    c.drawRightString(width - 2 * cm, y, f"Impuestos: ${float(factura.impuestos):,.0f}")
    y -= 16
    c.drawRightString(width - 2 * cm, y, f"Total: ${float(factura.total):,.0f}")

    y -= 35
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, y, "Este documento corresponde a una factura interna generada por SIGI-A.")
    y -= 12
    c.drawString(2 * cm, y, "No corresponde a facturación electrónica DIAN.")

    c.save()

    factura.nombre_archivo_pdf = nombre_archivo
    factura.ruta_pdf = ruta_pdf

    return ruta_pdf

@router.post("/generar", response_model=FacturaResponse)
def generar_factura(
    datos: FacturaCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin", "superadmin"])
    )
):
    pedido = db.query(Pedido).filter(
        Pedido.id_pedido == datos.id_pedido
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    if current_user.rol not in ["admin", "superadmin"]:
        if pedido.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para facturar este pedido"
            )

    factura_existente = db.query(Factura).filter(
        Factura.id_pedido == pedido.id_pedido
    ).first()

    if factura_existente:
        return factura_existente

    pago_aprobado = db.query(Pago).filter(
        Pago.id_pedido == pedido.id_pedido,
        Pago.estado_pago == "aprobado"
    ).first()

    if not pago_aprobado and pedido.estado != "pagado":
        raise HTTPException(
            status_code=400,
            detail="El pedido debe tener un pago aprobado antes de generar factura"
        )

    detalles = db.query(PedidoDetalle).filter(
        PedidoDetalle.id_pedido == pedido.id_pedido
    ).all()

    if not detalles:
        raise HTTPException(
            status_code=400,
            detail="El pedido no tiene detalle para facturar"
        )

    subtotal = sum([
        Decimal(detalle.subtotal or 0)
        for detalle in detalles
    ])

    impuestos = Decimal("0.00")
    total = Decimal(pedido.total or subtotal)

    cliente = db.query(Usuario).filter(
        Usuario.id_usuario == pedido.id_usuario
    ).first()

    correo_destino = datos.correo_destino

    if not correo_destino and cliente:
        correo_destino = cliente.correo

    nueva_factura = Factura(
        numero_factura=generar_numero_factura(pedido.id_pedido),
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        id_negocio=pedido.id_negocio,
        subtotal=subtotal,
        impuestos=impuestos,
        total=total,
        estado="emitida",
        correo_destino=correo_destino
    )

    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)

    return nueva_factura


@router.get("/", response_model=list[FacturaResponse])
def listar_facturas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin", "superadmin"])
    )
):
    if current_user.rol in ["admin", "superadmin"]:
        return db.query(Factura).order_by(
            Factura.id_factura.desc()
        ).all()

    return db.query(Factura).filter(
        Factura.id_usuario == current_user.id_usuario
    ).order_by(
        Factura.id_factura.desc()
    ).all()


@router.get("/{id_factura}", response_model=FacturaResponse)
def obtener_factura(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin", "superadmin"])
    )
):
    factura = db.query(Factura).filter(
        Factura.id_factura == id_factura
    ).first()

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada"
        )

    validar_acceso_factura(
        factura,
        current_user
    )

    return factura
@router.get("/{id_factura}/pdf")
def descargar_pdf_factura(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin", "superadmin"])
    )
):
    factura = db.query(Factura).filter(
        Factura.id_factura == id_factura
    ).first()

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada"
        )

    validar_acceso_factura(
        factura,
        current_user
    )

    ruta_pdf = factura.ruta_pdf

    if not ruta_pdf or not os.path.exists(ruta_pdf):
        ruta_pdf = generar_pdf_factura_archivo(
            db,
            factura
        )

        db.commit()
        db.refresh(factura)

    return FileResponse(
        path=ruta_pdf,
        filename=factura.nombre_archivo_pdf or f"{factura.numero_factura}.pdf",
        media_type="application/pdf"
    )

@router.post("/{id_factura}/enviar-correo")
def enviar_factura_por_correo(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin", "superadmin"])
    )
):
    factura = db.query(Factura).filter(
        Factura.id_factura == id_factura
    ).first()

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada"
        )

    validar_acceso_factura(
        factura,
        current_user
    )

    if not factura.correo_destino:
        cliente = db.query(Usuario).filter(
            Usuario.id_usuario == factura.id_usuario
        ).first()

        if cliente and cliente.correo:
            factura.correo_destino = cliente.correo
        else:
            raise HTTPException(
                status_code=400,
                detail="La factura no tiene correo destino"
            )

    ruta_pdf = factura.ruta_pdf

    if not ruta_pdf or not os.path.exists(ruta_pdf):
        ruta_pdf = generar_pdf_factura_archivo(
            db,
            factura
        )

    asunto = f"Factura {factura.numero_factura} - SIGI-A"

    cuerpo = f"""
Hola,

Adjuntamos tu factura generada en SIGI-A.

Número de factura: {factura.numero_factura}
Total: ${float(factura.total):,.0f}

Gracias por usar SIGI-A.
"""

    enviar_email_con_adjunto(
        destino=factura.correo_destino,
        asunto=asunto,
        cuerpo=cuerpo,
        ruta_adjunto=ruta_pdf,
        nombre_adjunto=factura.nombre_archivo_pdf or f"{factura.numero_factura}.pdf"
    )

    factura.estado = "enviada"
    factura.fecha_envio_correo = datetime.utcnow()

    db.commit()
    db.refresh(factura)

    return {
        "message": "Factura enviada por correo correctamente",
        "id_factura": factura.id_factura,
        "numero_factura": factura.numero_factura,
        "correo_destino": factura.correo_destino,
        "estado": factura.estado
    }

