from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, date

from app.database import get_db

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.calificacion import Calificacion
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita
from app.models.empleado import Empleado
from app.models.servicio import Servicio

from app.schemas.calificacion import (
    CalificacionCreate,
    CalificacionUpdate,
    CalificacionResponse,
    CitaPendienteCalificacion,
    RankingNegocio
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

    # ADMIN
    if current_user.rol == "admin":
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

    # ADMIN
    else:
        id_cliente = calificacion.id_cliente

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

    # ADMIN
    if current_user.rol == "admin":
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


# =========================
# CITAS PENDIENTES DE CALIFICAR
# =========================

@router.get("/citas-pendientes/all", response_model=List[CitaPendienteCalificacion])
def obtener_citas_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    """
    Obtiene citas finalizadas que aún no tienen calificación.
    Incluye información del negocio, empleado y servicio.
    """
    
    if current_user.rol == "admin":
        citas_sin_calificar = db.query(
            Cita.id_cita,
            Cita.id_negocio,
            Cita.id_empleado,
            Negocio.nombre_negocio,
            Empleado.nombre,
            Empleado.apellido,
            Servicio.nombre,
            Servicio.id_servicio,
            Cita.fecha,
            Cita.hora_inicio,
            Cita.hora_fin
        ).outerjoin(
            Calificacion,
            (Calificacion.id_cita == Cita.id_cita) & 
            (Calificacion.id_cliente == Cita.id_cliente)
        ).join(
            Negocio, Cita.id_negocio == Negocio.id_negocio
        ).join(
            Empleado, Cita.id_empleado == Empleado.id_empleado
        ).join(
            DetalleCita, Cita.id_cita == DetalleCita.id_cita
        ).join(
            Servicio, DetalleCita.id_servicio == Servicio.id_servicio
        ).filter(
            Calificacion.id_calificacion == None,
            Cita.estado == "completada"
        ).all()
    else:
        citas_sin_calificar = db.query(
            Cita.id_cita,
            Cita.id_negocio,
            Cita.id_empleado,
            Negocio.nombre_negocio,
            Empleado.nombre,
            Empleado.apellido,
            Servicio.nombre,
            Servicio.id_servicio,
            Cita.fecha,
            Cita.hora_inicio,
            Cita.hora_fin
        ).outerjoin(
            Calificacion,
            (Calificacion.id_cita == Cita.id_cita) & 
            (Calificacion.id_cliente == Cita.id_cliente)
        ).join(
            Negocio, Cita.id_negocio == Negocio.id_negocio
        ).join(
            Empleado, Cita.id_empleado == Empleado.id_empleado
        ).join(
            DetalleCita, Cita.id_cita == DetalleCita.id_cita
        ).join(
            Servicio, DetalleCita.id_servicio == Servicio.id_servicio
        ).filter(
            Cita.id_cliente == current_user.id_usuario,
            Calificacion.id_calificacion == None,
            Cita.estado == "completada"
        ).all()
    
    resultado = []
    for cita in citas_sin_calificar:
        resultado.append(CitaPendienteCalificacion(
            id_cita=cita.id_cita,
            id_negocio=cita.id_negocio,
            id_empleado=cita.id_empleado,
            negocio_nombre=cita.nombre_negocio,
            empleado_nombre=cita.nombre,
            empleado_apellido=cita.apellido,
            servicio_nombre=cita.nombre,
            servicio_id=cita.id_servicio,
            fecha=cita.fecha,
            hora_inicio=cita.hora_inicio,
            hora_fin=cita.hora_fin
        ))
    
    return resultado


# =========================
# RANKING DE NEGOCIOS
# =========================

@router.get("/ranking/all", response_model=List[RankingNegocio])
def obtener_ranking_negocios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin"])
    )
):
    """
    Obtiene el ranking de negocios ordenado por promedio de calificaciones.
    Incluye posición, nombre, promedio y cantidad de calificaciones.
    """
    
    ranking_data = db.query(
        Negocio.id_negocio,
        Negocio.nombre_negocio,
        func.avg(Calificacion.puntuacion).label("promedio"),
        func.count(Calificacion.id_calificacion).label("total_calificaciones")
    ).outerjoin(
        Calificacion, Negocio.id_negocio == Calificacion.id_negocio
    ).group_by(
        Negocio.id_negocio,
        Negocio.nombre_negocio
    ).order_by(
        func.avg(Calificacion.puntuacion).desc()
    ).all()
    
    resultado = []
    for posicion, (id_negocio, nombre_negocio, promedio, total) in enumerate(ranking_data, 1):
        resultado.append(RankingNegocio(
            posicion=posicion,
            id_negocio=id_negocio,
            nombre_negocio=nombre_negocio,
            promedio=round(float(promedio) if promedio else 0, 1),
            total_calificaciones=int(total) if total else 0
        ))
    
    return resultado