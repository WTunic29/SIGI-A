from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.auditoria import Auditoria
from app.models.user import Usuario

from app.schemas.auditoria import (
    AuditoriaCreate,
    AuditoriaResponse
)

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREAR LOG
# =========================

@router.post("/", response_model=AuditoriaResponse)
def crear_log(
    auditoria: AuditoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    nuevo = Auditoria(
        id_usuario=auditoria.id_usuario,
        accion=auditoria.accion,
        tabla_afectada=auditoria.tabla_afectada,
        id_registro=auditoria.id_registro,
        detalle=auditoria.detalle,
        fecha=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR LOGS
# =========================

@router.get("/", response_model=list[AuditoriaResponse])
def listar_logs(
    correo_usuario: str | None = None,
    accion: str | None = None,
    modulo: str | None = None,
    resultado: str | None = None,
    nivel: str | None = None,
    limite: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):
    query = db.query(Auditoria)

    if correo_usuario:
        query = query.filter(
            Auditoria.correo_usuario.ilike(f"%{correo_usuario}%")
        )

    if accion:
        query = query.filter(
            Auditoria.accion.ilike(f"%{accion}%")
        )

    if modulo:
        query = query.filter(
            Auditoria.modulo.ilike(f"%{modulo}%")
        )

    if resultado:
        query = query.filter(
            Auditoria.resultado == resultado
        )

    if nivel:
        query = query.filter(
            Auditoria.nivel == nivel
        )

    return (
        query
        .order_by(Auditoria.id_auditoria.desc())
        .limit(limite)
        .all()
    )

# =========================
# OBTENER LOG
# =========================

@router.get("/{id_auditoria}", response_model=AuditoriaResponse)
def obtener_log(
    id_auditoria: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    log = db.query(Auditoria).filter(
        Auditoria.id_auditoria == id_auditoria
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Log no encontrado"
        )

    return log


# =========================
# ELIMINAR LOG
# =========================

@router.delete("/{id_auditoria}")
def eliminar_log(
    id_auditoria: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["admin"])
    )
):

    log = db.query(Auditoria).filter(
        Auditoria.id_auditoria == id_auditoria
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Log no encontrado"
        )

    db.delete(log)
    db.commit()

    return {
        "message": "Log eliminado"
    }
