
import os
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from typing import Optional
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
    current_user: Usuario,
    db: Session
):
    if current_user.rol in ["admin", "superadmin"]:
        return

    if current_user.rol == "cliente" and factura.id_usuario == current_user.id_usuario:
        return

    if current_user.rol == "negocio":
        negocio = db.query(Negocio).filter(
            Negocio.id_negocio == factura.id_negocio,
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if negocio:
            return

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

    pago = db.query(Pago).filter(
        Pago.id_pedido == factura.id_pedido,
        Pago.estado_pago == "aprobado"
    ).order_by(Pago.id_pago.desc()).first()

    nombre_archivo = f"{factura.numero_factura}.pdf"
    ruta_pdf = os.path.join(FACTURAS_DIR, nombre_archivo)

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter

    negro = colors.HexColor("#0B0B0B")
    dorado = colors.HexColor("#D6B84A")
    dorado_suave = colors.HexColor("#F4E6A6")
    gris = colors.HexColor("#555555")
    gris_claro = colors.HexColor("#F4F4F4")
    blanco = colors.white

    def money(value):
        try:
            return f"${float(value or 0):,.0f}".replace(",", ".")
        except Exception:
            return "$0"

    def safe(value, default="N/A"):
        return str(value) if value not in [None, ""] else default

    def draw_card(x, y, w, h, titulo, lineas):
        c.setFillColor(gris_claro)
        c.roundRect(x, y - h, w, h, 10, fill=1, stroke=0)

        c.setFillColor(negro)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 0.35 * cm, y - 0.55 * cm, titulo)

        c.setFillColor(gris)
        c.setFont("Helvetica", 8.5)

        yy = y - 0.95 * cm
        for linea in lineas:
            c.drawString(x + 0.35 * cm, yy, str(linea)[:58])
            yy -= 0.38 * cm

    y = height

    # Header
    c.setFillColor(negro)
    c.rect(0, height - 3.4 * cm, width, 3.4 * cm, fill=1, stroke=0)

    c.setFillColor(dorado)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(2 * cm, height - 1.35 * cm, "SIGI-E")

    c.setFillColor(blanco)
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, height - 1.82 * cm, "Sistema inteligente de gestión integral")
    c.drawString(2 * cm, height - 2.25 * cm, "NIT: 902224021-M")

    c.setFillColor(dorado)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 2 * cm, height - 1.25 * cm, "FACTURA / COMPROBANTE")

    c.setFillColor(blanco)
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 2 * cm, height - 1.75 * cm, factura.numero_factura)
    c.drawRightString(width - 2 * cm, height - 2.18 * cm, f"Pedido #{factura.id_pedido}")
    c.drawRightString(width - 2 * cm, height - 2.62 * cm, f"Fecha: {safe(factura.fecha_emision)}")

    y = height - 4.1 * cm

    # Cards
    nombre_cliente = f"{safe(getattr(cliente, 'nombre', ''), '')} {safe(getattr(cliente, 'apellido', ''), '')}".strip() or "N/A"
    nombre_negocio = safe(getattr(negocio, "nombre_negocio", None))

    draw_card(
        2 * cm,
        y,
        8.2 * cm,
        2.8 * cm,
        "Datos del cliente",
        [
            f"Cliente: {nombre_cliente}",
            f"Correo: {safe(getattr(cliente, 'correo', None))}",
            f"Teléfono: {safe(getattr(cliente, 'telefono', None))}",
        ]
    )

    draw_card(
        10.7 * cm,
        y,
        8.2 * cm,
        2.8 * cm,
        "Datos del negocio",
        [
            f"Negocio: {nombre_negocio}",
            f"Correo: {safe(getattr(negocio, 'email_negocio', None))}",
            f"Teléfono: {safe(getattr(negocio, 'telefono', None))}",
            f"Dirección: {safe(getattr(negocio, 'direccion', None))}",
        ]
    )

    y -= 3.6 * cm

    # Pago
    metodo_pago = safe(getattr(pago, "metodo_pago", None), "No registrado")
    estado_pago = safe(getattr(pago, "estado_pago", None), safe(getattr(pedido, "estado", None), "N/A"))
    referencia = safe(getattr(pago, "referencia_externa", None), "N/A")

    c.setFillColor(dorado_suave)
    c.roundRect(2 * cm, y - 1.1 * cm, width - 4 * cm, 1.1 * cm, 8, fill=1, stroke=0)

    c.setFillColor(negro)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.35 * cm, y - 0.42 * cm, f"Método de pago: {metodo_pago.upper()}")
    c.drawString(8 * cm, y - 0.42 * cm, f"Estado: {estado_pago.upper()}")
    c.drawString(12.4 * cm, y - 0.42 * cm, f"Referencia: {referencia[:25]}")

    y -= 1.8 * cm

    # Tabla encabezado
    c.setFillColor(negro)
    c.roundRect(2 * cm, y - 0.75 * cm, width - 4 * cm, 0.75 * cm, 6, fill=1, stroke=0)

    c.setFillColor(dorado)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.35 * cm, y - 0.48 * cm, "Descripción")
    c.drawRightString(12 * cm, y - 0.48 * cm, "Cant.")
    c.drawRightString(15 * cm, y - 0.48 * cm, "Precio")
    c.drawRightString(width - 2.35 * cm, y - 0.48 * cm, "Subtotal")

    y -= 1.1 * cm

    c.setFont("Helvetica", 9)
    c.setFillColor(negro)

    for idx, detalle in enumerate(detalles, start=1):
        if y < 4.5 * cm:
            c.showPage()
            y = height - 2 * cm

        nombre_item = obtener_nombre_item(db, detalle)
        tipo = safe(getattr(detalle, "tipo_item", None), "item").capitalize()

        if idx % 2 == 0:
            c.setFillColor(colors.HexColor("#FAFAFA"))
            c.rect(2 * cm, y - 0.45 * cm, width - 4 * cm, 0.62 * cm, fill=1, stroke=0)

        c.setFillColor(negro)
        c.drawString(2.35 * cm, y - 0.20 * cm, f"{tipo}: {str(nombre_item)[:44]}")
        c.drawRightString(12 * cm, y - 0.20 * cm, str(detalle.cantidad))
        c.drawRightString(15 * cm, y - 0.20 * cm, money(detalle.precio_unitario))
        c.drawRightString(width - 2.35 * cm, y - 0.20 * cm, money(detalle.subtotal))
        y -= 0.72 * cm

    y -= 0.35 * cm

    # Totales
    box_x = width - 8 * cm
    box_w = 6 * cm
    box_h = 2.7 * cm

    c.setFillColor(gris_claro)
    c.roundRect(box_x, y - box_h, box_w, box_h, 8, fill=1, stroke=0)

    c.setFillColor(negro)
    c.setFont("Helvetica", 9)
    c.drawRightString(box_x + box_w - 0.35 * cm, y - 0.55 * cm, f"Subtotal: {money(factura.subtotal)}")
    c.drawRightString(box_x + box_w - 0.35 * cm, y - 1.05 * cm, f"Impuestos: {money(factura.impuestos)}")

    c.setFillColor(dorado)
    c.roundRect(box_x + 0.25 * cm, y - 2.35 * cm, box_w - 0.5 * cm, 0.8 * cm, 6, fill=1, stroke=0)

    c.setFillColor(negro)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(box_x + box_w - 0.5 * cm, y - 1.85 * cm, f"TOTAL: {money(factura.total)}")

    # Footer
    c.setFillColor(gris)
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 2.1 * cm, "Este documento corresponde a un comprobante interno generado por SIGI-E.")
    c.drawString(2 * cm, 1.75 * cm, "No corresponde a facturación electrónica DIAN.")
    c.drawString(2 * cm, 1.4 * cm, "Gracias por usar SIGI-E.")

    c.setFillColor(dorado)
    c.rect(0, 0, width, 0.35 * cm, fill=1, stroke=0)

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
        require_roles(["cliente", "negocio", "admin", "superadmin"])
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
    id_negocio: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin", "superadmin"])
    )
):
    if current_user.rol in ["admin", "superadmin"]:
        query = db.query(Factura)
        if id_negocio:
            query = query.filter(Factura.id_negocio == id_negocio)
        return query.order_by(Factura.id_factura.desc()).all()

    if current_user.rol == "cliente":
        return db.query(Factura).filter(
            Factura.id_usuario == current_user.id_usuario
        ).order_by(
            Factura.id_factura.desc()
        ).all()

    negocios_propios = db.query(Negocio.id_negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).all()

    ids_negocios = [n.id_negocio for n in negocios_propios]

    if id_negocio:
        if id_negocio not in ids_negocios:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para consultar facturas de este negocio"
            )
        ids_negocios = [id_negocio]

    return db.query(Factura).filter(
        Factura.id_negocio.in_(ids_negocios)
    ).order_by(
        Factura.id_factura.desc()
    ).all()


@router.get("/{id_factura}", response_model=FacturaResponse)
def obtener_factura(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin", "superadmin"])
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
        current_user,
        db
    )

    return factura
@router.get("/{id_factura}/pdf")
def descargar_pdf_factura(
    id_factura: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin", "superadmin"])
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
        current_user,
        db
    )

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
        require_roles(["cliente", "negocio", "admin", "superadmin"])
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
        current_user,
        db
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

