from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
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


@router.post("/", response_model=CitaResponse)
def crear_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    cita_existente = db.query(Cita).filter(
        Cita.id_empleado == cita.id_empleado,
        Cita.fecha == cita.fecha,
        Cita.hora_inicio < cita.hora_fin,
        Cita.hora_fin > cita.hora_inicio,
        Cita.estado != "cancelada"
    ).first()

    if cita_existente:
        raise HTTPException(
            status_code=400,
            detail="El empleado ya tiene una cita en ese horario"
        )

    nueva_cita = Cita(
        id_cliente=cita.id_cliente,
        id_negocio=cita.id_negocio,
        id_empleado=cita.id_empleado,
        fecha=cita.fecha,
        hora_inicio=cita.hora_inicio,
        hora_fin=cita.hora_fin,
        estado="pendiente",
        observaciones=cita.observaciones
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)

    return nueva_cita


@router.get("/negocio/{id_negocio}", response_model=List[CitaResponse])
def listar_citas_negocio(id_negocio: int, db: Session = Depends(get_db)):
    return db.query(Cita).filter(Cita.id_negocio == id_negocio).all()


@router.get("/empleado/{id_empleado}", response_model=List[CitaResponse])
def listar_citas_empleado(id_empleado: int, db: Session = Depends(get_db)):
    return db.query(Cita).filter(Cita.id_empleado == id_empleado).all()


@router.get("/cliente/{id_cliente}", response_model=List[CitaResponse])
def listar_citas_cliente(id_cliente: int, db: Session = Depends(get_db)):
    return db.query(Cita).filter(Cita.id_cliente == id_cliente).all()


@router.put("/{id_cita}", response_model=CitaResponse)
def actualizar_cita(
    id_cita: int,
    cita: CitaUpdate,
    db: Session = Depends(get_db)
):
    cita_db = db.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita_db:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    datos = cita.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(cita_db, campo, valor)

    db.commit()
    db.refresh(cita_db)

    return cita_db


@router.delete("/{id_cita}")
def cancelar_cita(id_cita: int, db: Session = Depends(get_db)):
    cita_db = db.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita_db:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita_db.estado = "cancelada"
    db.commit()

    return {"message": "Cita cancelada correctamente"}


@router.post("/{id_cita}/detalle", response_model=DetalleCitaResponse)
def agregar_detalle_cita(
    id_cita: int,
    detalle: DetalleCitaCreate,
    db: Session = Depends(get_db)
):
    cita_db = db.query(Cita).filter(Cita.id_cita == id_cita).first()

    if not cita_db:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

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
def listar_detalle_cita(id_cita: int, db: Session = Depends(get_db)):
    return db.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()