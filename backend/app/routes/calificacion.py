from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from app.database import get_db

from app.core.deps import require_roles

from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita
from app.models.servicio import Servicio
from app.models.empleado import Empleado
from app.models.calificacion import Calificacion
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.calificacion import (
    CalificacionCreate,
    CalificacionUpdate,
    CalificacionResponse,
    RankingNegocio,
    CitaPendienteCalificacion
)

router = APIRouter()


# =========================
# VALIDAR ACCESO
# =========================

def validar_acceso_calificacion(
    calificacion: Calificacion,
    current_user: Usuario,
    db: Session
):

    # ADMIN / SUPERADMIN
    if current_user.rol in ["admin", "superadmin"]:
        return

    # CLIENTE
    if current_user.rol == "cliente":

        if calificacion.id_cliente != current_user.id_usuario:
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

        if calificacion.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No autorizado"
            )


# =========================
# CREAR CALIFICACION
# =========================

@router.post("/", response_model=CalificacionResponse)
def crear_calificacion(
    calificacion: CalificacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    if calificacion.puntuacion < 1 or calificacion.puntuacion > 5:
        raise HTTPException(
            status_code=400,
            detail="La puntuación debe estar entre 1 y 5"
        )

    # CLIENTE
    if current_user.rol == "cliente":
        id_cliente = current_user.id_usuario

    # ADMIN / SUPERADMIN
    else:
        id_cliente = calificacion.id_cliente

        if not id_cliente:
            raise HTTPException(
                status_code=400,
                detail="id_cliente es obligatorio para crear una calificación como administrador"
            )

    cita_db = db.query(Cita).filter(
        Cita.id_cita == calificacion.id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente" and cita_db.id_cliente != id_cliente:
        raise HTTPException(
            status_code=403,
            detail="No puedes calificar una cita de otro usuario"
        )

    if cita_db.id_negocio != calificacion.id_negocio:
        raise HTTPException(
            status_code=400,
            detail="La cita no pertenece al negocio enviado"
        )

    if cita_db.estado not in ["finalizada", "completada", "atendida"]:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes calificar citas finalizadas"
        )

    calificacion_existente = db.query(Calificacion).filter(
        Calificacion.id_cita == calificacion.id_cita,
        Calificacion.id_cliente == id_cliente
    ).first()

    if calificacion_existente:
        raise HTTPException(
            status_code=400,
            detail="Esta cita ya fue calificada"
        )

    cita_db = db.query(Cita).filter(
        Cita.id_cita == calificacion.id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente" and cita_db.id_cliente != id_cliente:
        raise HTTPException(
            status_code=403,
            detail="No puedes calificar una cita de otro usuario"
        )

    if cita_db.id_negocio != calificacion.id_negocio:
        raise HTTPException(
            status_code=400,
            detail="La cita no pertenece al negocio enviado"
        )

    if cita_db.estado not in ["finalizada", "completada", "atendida"]:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes calificar citas finalizadas"
        )

    calificacion_existente = db.query(Calificacion).filter(
        Calificacion.id_cita == calificacion.id_cita,
        Calificacion.id_cliente == id_cliente
    ).first()

    if calificacion_existente:
        raise HTTPException(
            status_code=400,
            detail="Esta cita ya fue calificada"
        )

    nueva_calificacion = Calificacion(
        id_cliente=id_cliente,
        id_negocio=calificacion.id_negocio,
        id_cita=calificacion.id_cita,
        puntuacion=calificacion.puntuacion,
        comentario=calificacion.comentario
    )

    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)

    return nueva_calificacion


# =========================
# LISTAR CALIFICACIONES
# =========================

@router.get("/", response_model=List[CalificacionResponse])
def listar_calificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    # ADMIN / SUPERADMIN
    if current_user.rol in ["admin", "superadmin"]:
        return db.query(Calificacion).all()

    # CLIENTE
    if current_user.rol == "cliente":

        return db.query(Calificacion).filter(
            Calificacion.id_cliente == current_user.id_usuario
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

    return db.query(Calificacion).filter(
        Calificacion.id_negocio == negocio.id_negocio
    ).all()


# =========================
# RANKING DE NEGOCIOS
# =========================

@router.get("/ranking/all", response_model=List[RankingNegocio])
def ranking_negocios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    resultados = (
        db.query(
            Calificacion.id_negocio.label("id_negocio"),
            Negocio.nombre_negocio.label("nombre_negocio"),
            func.avg(Calificacion.puntuacion).label("promedio"),
            func.count(Calificacion.id_calificacion).label("total_calificaciones")
        )
        .join(Negocio, Negocio.id_negocio == Calificacion.id_negocio)
        .group_by(Calificacion.id_negocio, Negocio.nombre_negocio)
        .order_by(
            desc(func.avg(Calificacion.puntuacion)),
            desc(func.count(Calificacion.id_calificacion)),
            Negocio.nombre_negocio.asc()
        )
        .all()
    )

    ranking = []

    for index, item in enumerate(resultados, start=1):
        ranking.append({
            "posicion": index,
            "id_negocio": int(item.id_negocio),
            "nombre_negocio": item.nombre_negocio,
            "promedio": round(float(item.promedio or 0), 2),
            "total_calificaciones": int(item.total_calificaciones or 0)
        })

    return ranking

# =========================
# CITAS PENDIENTES POR CALIFICAR
# =========================

@router.get("/citas-pendientes/all", response_model=List[CitaPendienteCalificacion])
def citas_pendientes_calificar(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    estados_finalizados = ["finalizada", "completada", "atendida"]

    query = (
        db.query(
            Cita.id_cita.label("id_cita"),
            Cita.id_negocio.label("id_negocio"),
            Cita.id_empleado.label("id_empleado"),
            Negocio.nombre_negocio.label("negocio_nombre"),
            Empleado.nombre.label("empleado_nombre"),
            Empleado.apellido.label("empleado_apellido"),
            Servicio.nombre.label("servicio_nombre"),
            Servicio.id_servicio.label("servicio_id"),
            Cita.fecha.label("fecha"),
            Cita.hora_inicio.label("hora_inicio"),
            Cita.hora_fin.label("hora_fin")
        )
        .join(Negocio, Negocio.id_negocio == Cita.id_negocio)
        .join(Empleado, Empleado.id_empleado == Cita.id_empleado)
        .join(DetalleCita, DetalleCita.id_cita == Cita.id_cita)
        .join(Servicio, Servicio.id_servicio == DetalleCita.id_servicio)
        .outerjoin(Calificacion, Calificacion.id_cita == Cita.id_cita)
        .filter(Cita.estado.in_(estados_finalizados))
        .filter(Calificacion.id_calificacion.is_(None))
    )

    if current_user.rol == "cliente":
        query = query.filter(Cita.id_cliente == current_user.id_usuario)

    resultados = query.order_by(Cita.fecha.desc(), Cita.hora_inicio.desc()).all()

    return [
        {
            "id_cita": int(item.id_cita),
            "id_negocio": int(item.id_negocio),
            "id_empleado": int(item.id_empleado) if item.id_empleado else None,
            "negocio_nombre": item.negocio_nombre,
            "empleado_nombre": item.empleado_nombre,
            "empleado_apellido": item.empleado_apellido,
            "servicio_nombre": item.servicio_nombre,
            "servicio_id": int(item.servicio_id) if item.servicio_id else None,
            "fecha": item.fecha,
            "hora_inicio": item.hora_inicio,
            "hora_fin": item.hora_fin
        }
        for item in resultados
    ]

# =========================
# OBTENER CALIFICACION
# =========================

@router.get("/{id_calificacion}", response_model=CalificacionResponse)
def obtener_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):

    calificacion = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion,
        current_user,
        db
    )

    return calificacion


# =========================
# ACTUALIZAR CALIFICACION
# =========================

@router.put("/{id_calificacion}", response_model=CalificacionResponse)
def actualizar_calificacion(
    id_calificacion: int,
    calificacion: CalificacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion_db,
        current_user,
        db
    )

    datos = calificacion.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(calificacion_db, campo, valor)

    db.commit()
    db.refresh(calificacion_db)

    return calificacion_db


# =========================
# ELIMINAR CALIFICACION
# =========================

@router.delete("/{id_calificacion}")
def eliminar_calificacion(
    id_calificacion: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    calificacion_db = db.query(Calificacion).filter(
        Calificacion.id_calificacion == id_calificacion
    ).first()

    if not calificacion_db:
        raise HTTPException(
            status_code=404,
            detail="Calificación no encontrada"
        )

    validar_acceso_calificacion(
        calificacion_db,
        current_user,
        db
    )

    db.delete(calificacion_db)
    db.commit()

    return {
        "message": "Calificación eliminada correctamente"
    }
