from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.core.deps import require_roles
from app.models.user import Usuario
from app.models.negocio import Negocio


router = APIRouter()


def validar_acceso_dashboard_negocio(
    db: Session,
    current_user: Usuario,
    id_negocio: int
):
    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == id_negocio
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado"
        )

    if current_user.rol in ["admin", "superadmin"]:
        return negocio

    if current_user.rol == "negocio" and negocio.id_usuario_propietario == current_user.id_usuario:
        return negocio

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para consultar métricas de este negocio"
    )


def rows_to_list(result):
    return [dict(row._mapping) for row in result]


@router.get("/negocio/{id_negocio}/metricas")
def obtener_metricas_negocio(
    id_negocio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin", "superadmin"]))
):
    negocio = validar_acceso_dashboard_negocio(db, current_user, id_negocio)

    resumen = db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM core.citas WHERE id_negocio = :id_negocio) AS total_citas,
            (SELECT COUNT(*) FROM core.empleados WHERE id_negocio = :id_negocio AND estado = 'activo') AS total_empleados_activos,
            (SELECT COUNT(*) FROM core.productos WHERE id_negocio = :id_negocio AND estado = 'activo') AS total_productos_activos,
            (SELECT COUNT(*) FROM core.servicios WHERE id_negocio = :id_negocio AND estado = 'activo') AS total_servicios_activos,
            (SELECT COUNT(*) FROM core.productos WHERE id_negocio = :id_negocio AND stock <= 5 AND estado = 'activo') AS productos_stock_bajo,
            COALESCE((
                SELECT SUM(total)
                FROM core.pedidos
                WHERE id_negocio = :id_negocio
                AND estado IN ('pagado', 'entregado')
                AND fecha >= date_trunc('month', CURRENT_DATE)
            ), 0) AS ingresos_mes,
            COALESCE((
                SELECT COUNT(*)
                FROM core.pedidos
                WHERE id_negocio = :id_negocio
                AND estado IN ('pagado', 'entregado')
                AND fecha >= date_trunc('month', CURRENT_DATE)
            ), 0) AS pedidos_mes
    """), {"id_negocio": id_negocio}).first()._mapping

    citas_por_mes = rows_to_list(db.execute(text("""
        SELECT
            TO_CHAR(date_trunc('month', fecha), 'YYYY-MM') AS mes,
            COUNT(*) AS total
        FROM core.citas
        WHERE id_negocio = :id_negocio
        GROUP BY date_trunc('month', fecha)
        ORDER BY date_trunc('month', fecha)
    """), {"id_negocio": id_negocio}))

    estados_citas = rows_to_list(db.execute(text("""
        SELECT
            estado,
            COUNT(*) AS total
        FROM core.citas
        WHERE id_negocio = :id_negocio
        GROUP BY estado
        ORDER BY total DESC
    """), {"id_negocio": id_negocio}))

    top_empleados = rows_to_list(db.execute(text("""
        SELECT
            e.id_empleado,
            e.nombre || ' ' || e.apellido AS empleado,
            e.especialidad,
            COUNT(c.id_cita) AS total_citas,
            COUNT(c.id_cita) FILTER (WHERE c.estado IN ('confirmada', 'finalizada', 'completada')) AS citas_exitosas,
            COUNT(c.id_cita) FILTER (WHERE c.estado IN ('cancelada', 'anulada', 'rechazada', 'no_asistio')) AS citas_perdidas,
            COALESCE(SUM(dc.precio) FILTER (WHERE c.estado IN ('confirmada', 'finalizada', 'completada')), 0) AS ingresos_generados
        FROM core.empleados e
        LEFT JOIN core.citas c ON c.id_empleado = e.id_empleado
        LEFT JOIN core.detalle_cita dc ON dc.id_cita = c.id_cita
        WHERE e.id_negocio = :id_negocio
        GROUP BY e.id_empleado, e.nombre, e.apellido, e.especialidad
        ORDER BY citas_exitosas DESC, ingresos_generados DESC, total_citas DESC
        LIMIT 5
    """), {"id_negocio": id_negocio}))

    productos_mas_vendidos = rows_to_list(db.execute(text("""
        SELECT
            p.id_producto,
            p.nombre,
            COALESCE(SUM(pd.cantidad), 0) AS unidades_vendidas,
            COALESCE(SUM(pd.subtotal), 0) AS total_vendido
        FROM core.productos p
        LEFT JOIN core.pedido_detalle pd ON pd.id_producto = p.id_producto AND pd.tipo_item = 'producto'
        LEFT JOIN core.pedidos pe ON pe.id_pedido = pd.id_pedido AND pe.estado IN ('pagado', 'entregado')
        WHERE p.id_negocio = :id_negocio
        GROUP BY p.id_producto, p.nombre
        ORDER BY unidades_vendidas DESC, total_vendido DESC
        LIMIT 5
    """), {"id_negocio": id_negocio}))

    ventas_por_mes = rows_to_list(db.execute(text("""
        SELECT
            TO_CHAR(date_trunc('month', fecha), 'YYYY-MM') AS mes,
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS total_ventas
        FROM core.pedidos
        WHERE id_negocio = :id_negocio
        AND estado IN ('pagado', 'entregado')
        GROUP BY date_trunc('month', fecha)
        ORDER BY date_trunc('month', fecha)
    """), {"id_negocio": id_negocio}))

    servicios_mas_agendados = rows_to_list(db.execute(text("""
        SELECT
            s.id_servicio,
            s.nombre,
            COUNT(dc.id_detalle_cita) AS total_agendado,
            COALESCE(SUM(dc.precio), 0) AS ingresos_servicio
        FROM core.servicios s
        LEFT JOIN core.detalle_cita dc ON dc.id_servicio = s.id_servicio
        LEFT JOIN core.citas c ON c.id_cita = dc.id_cita
        WHERE s.id_negocio = :id_negocio
        GROUP BY s.id_servicio, s.nombre
        ORDER BY total_agendado DESC, ingresos_servicio DESC
        LIMIT 5
    """), {"id_negocio": id_negocio}))

    inventario_bajo = rows_to_list(db.execute(text("""
        SELECT
            id_producto,
            nombre,
            stock,
            precio,
            estado
        FROM core.productos
        WHERE id_negocio = :id_negocio
        AND stock <= 5
        ORDER BY stock ASC, nombre ASC
        LIMIT 10
    """), {"id_negocio": id_negocio}))

    return {
        "negocio": {
            "id_negocio": negocio.id_negocio,
            "nombre_negocio": negocio.nombre_negocio
        },
        "resumen": dict(resumen),
        "citas_por_mes": citas_por_mes,
        "estados_citas": estados_citas,
        "top_empleados": top_empleados,
        "productos_mas_vendidos": productos_mas_vendidos,
        "ventas_por_mes": ventas_por_mes,
        "servicios_mas_agendados": servicios_mas_agendados,
        "inventario_bajo": inventario_bajo
    }
