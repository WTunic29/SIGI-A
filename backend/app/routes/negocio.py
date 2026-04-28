from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.schemas.negocio import NegocioCreate
from app.core.deps import require_role

router = APIRouter()


@router.post("/", status_code=201)
def crear_negocio(
    negocio: NegocioCreate,
    current_user: Usuario = Depends(require_role("negocio")),
    db: Session = Depends(get_db)
):
    existente = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Este usuario ya tiene un negocio registrado"
        )

    nuevo_negocio = Negocio(
        id_usuario_propietario=current_user.id_usuario,
        nombre_negocio=negocio.nombre,
        descripcion=negocio.descripcion,
        direccion=negocio.direccion,
        telefono=negocio.telefono,
        email_negocio=negocio.correo
    )

    db.add(nuevo_negocio)
    db.commit()
    db.refresh(nuevo_negocio)

    return {
        "message": "Negocio creado correctamente",
        "negocio": {
            "id": nuevo_negocio.id_negocio,
            "nombre": nuevo_negocio.nombre_negocio,
            "descripcion": nuevo_negocio.descripcion,
            "direccion": nuevo_negocio.direccion,
            "telefono": nuevo_negocio.telefono,
            "correo": nuevo_negocio.email_negocio
        }
    }


@router.get("/")
def listar_negocios(db: Session = Depends(get_db)):
    negocios = db.query(Negocio).all()

    return negocios