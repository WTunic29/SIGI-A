from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.core.deps import require_roles
from app.models.user import Usuario
from app.models.negocio import Negocio
from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita
from app.schemas.cita import (
    CitaCreate,
    CitaUpdate,
    CitaResponse,
    DetalleCitaCreate,
    DetalleCitaResponse
)

router = APIRouter()


def obtener_negocio_usuario(db: Session, id_usuario: int, id_negocio: int):
    return db.query(Negocio).filter(
        Negocio.id_usuario_propietario == id_usuario,
        Negocio.id_negocio == id_negocio
    ).first()


@router.post("/", response_model=dict)
def crear_cita(
    cita: CitaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "admin"]))
):
    fecha_hora_inicio = datetime.combine(cita.fecha, cita.hora_inicio)
    fecha_hora_fin = datetime.combine(cita.fecha, cita.hora_fin)

    if fecha_hora_fin <= fecha_hora_inicio:
        raise HTTPException(
            status_code=400,
            detail="La hora fin debe ser mayor a la hora inicio"
        )

    cita_existente = db.query(Cita).filter(
        Cita.id_empleado == cita.id_empleado,
        Cita.fecha_hora_inicio < fecha_hora_fin,
        Cita.fecha_hora_fin > fecha_hora_inicio,
        Cita.estado != "cancelada"
    ).first()

    if cita_existente:
        raise HTTPException(
            status_code=400,
            detail="El empleado ya tiene una cita en ese horario"
        )

    nueva_cita = Cita(
        id_cliente=current_user.id_usuario,
        id_negocio=cita.id_negocio,
        id_empleado=cita.id_empleado,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado="pendiente",
        observaciones=cita.observaciones
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)

    return {
        "id_cita": nueva_cita.id_cita,
        "id_cliente": nueva_cita.id_cliente,
        "id_negocio": nueva_cita.id_negocio,
        "id_empleado": nueva_cita.id_empleado,
        "fecha_hora_inicio": nueva_cita.fecha_hora_inicio,
        "fecha_hora_fin": nueva_cita.fecha_hora_fin,
        "estado": nueva_cita.estado,
        "observaciones": nueva_cita.observaciones,
        "message": "Cita creada correctamente"
    }

@router.get("/negocio/{id_negocio}", response_model=List[CitaResponse])
def listar_citas_negocio(
    id_negocio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin"]))
):
    negocio = obtener_negocio_usuario(
        db,
        current_user.id_usuario,
        id_negocio
    )

    if not negocio:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver citas de este negocio"
        )

    return db.query(Cita).filter(
        Cita.id_negocio == id_negocio
    ).all()


@router.get("/empleado/{id_empleado}", response_model=List[CitaResponse])
def listar_citas_empleado(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin"]))
):
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=403,
            detail="No tienes negocio registrado"
        )

    return db.query(Cita).filter(
        Cita.id_empleado == id_empleado,
        Cita.id_negocio == negocio.id_negocio
    ).all()


@router.get("/cliente/{id_cliente}", response_model=List[CitaResponse])
def listar_citas_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin"]))
):
    if current_user.rol == "cliente":
        if id_cliente != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No puedes ver citas de otro cliente"
            )

    return db.query(Cita).filter(
        Cita.id_cliente == id_cliente
    ).all()


@router.put("/{id_cita}", response_model=CitaResponse)
def actualizar_cita(
    id_cita: int,
    cita: CitaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    negocio = obtener_negocio_usuario(
        db,
        current_user.id_usuario,
        cita_db.id_negocio
    )

    if not negocio:
        raise HTTPException(
            status_code=403,
            detail="No puedes modificar esta cita"
        )

    datos = cita.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(cita_db, campo, valor)

    db.commit()
    db.refresh(cita_db)

    return cita_db


@router.delete("/{id_cita}")
def cancelar_cita(
    id_cita: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente":
        if cita_db.id_cliente != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No puedes cancelar esta cita"
            )

    if current_user.rol == "negocio":
        negocio = obtener_negocio_usuario(
            db,
            current_user.id_usuario,
            cita_db.id_negocio
        )

        if not negocio:
            raise HTTPException(
                status_code=403,
                detail="No puedes cancelar esta cita"
            )

    cita_db.estado = "cancelada"
    db.commit()

    return {"message": "Cita cancelada correctamente"}


@router.post("/{id_cita}/detalle", response_model=DetalleCitaResponse)
def agregar_detalle_cita(
    id_cita: int,
    detalle: DetalleCitaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente":
        if cita_db.id_cliente != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No puedes agregar detalle a esta cita"
            )

    if current_user.rol == "negocio":
        negocio = obtener_negocio_usuario(
            db,
            current_user.id_usuario,
            cita_db.id_negocio
        )

        if not negocio:
            raise HTTPException(
                status_code=403,
                detail="No puedes agregar detalle a esta cita"
            )

    nuevo_detalle = DetalleCita(
        id_cita=id_cita,
        id_servicio=detalle.id_servicio,
        precio=detalle.precio,
        duracion=detalle.duracion
    )

    db.add(nuevo_detalle)
    db.commit()
    db.refresh(nuevo_detalle)

    return nuevo_detalle


@router.get("/{id_cita}/detalle", response_model=List[DetalleCitaResponse])
def listar_detalle_cita(
    id_cita: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente":
        if cita_db.id_cliente != current_user.id_usuario:
            raise HTTPException(
                status_code=403,
                detail="No puedes ver este detalle"
            )

    if current_user.rol == "negocio":
        negocio = obtener_negocio_usuario(
            db,
            current_user.id_usuario,
            cita_db.id_negocio
        )

        if not negocio:
            raise HTTPException(
                status_code=403,
                detail="No puedes ver este detalle"
            )

    return db.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()