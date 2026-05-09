from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.servicio import Servicio
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.schemas.servicio import ServicioCreate
from app.core.deps import require_role

router = APIRouter()


@router.post("/", status_code=201)
def crear_servicio(
    servicio: ServicioCreate,
    current_user: Usuario = Depends(require_role("negocio")),
    db: Session = Depends(get_db)
):
    # 🔥 buscar negocio del usuario
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(status_code=404, detail="No tienes un negocio registrado")

    nuevo_servicio = Servicio(
        id_negocio=negocio.id_negocio,
        nombre=servicio.nombre,
        descripcion=servicio.descripcion,
        duracion_minutos=servicio.duracion_minutos,
        precio=servicio.precio,
        estado="activo",
        imagen_url=servicio.imagen_url
    )

    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return {
        "message": "Servicio creado correctamente",
        "servicio": {
            "id": nuevo_servicio.id_servicio,
            "nombre": nuevo_servicio.nombre,
            "precio": float(nuevo_servicio.precio),
            "duracion": nuevo_servicio.duracion_minutos
        }
    }


@router.get("/{id_negocio}")
def listar_servicios(id_negocio: int, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).filter(
        Servicio.id_negocio == id_negocio,
        Servicio.estado == "activo"
    ).all()

    return servicios