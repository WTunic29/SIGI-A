from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.deps import (
    require_roles
)

from app.models.servicio import Servicio
from app.models.negocio import Negocio
from app.models.user import Usuario

from app.schemas.servicio import (
    ServicioCreate,
    ServicioUpdate,
    ServicioResponse
)

from app.utils.auditoria import registrar_auditoria

router = APIRouter()


# =========================
# VALIDAR ACCESO SERVICIO
# =========================

def validar_acceso_servicio(
    servicio: Servicio,
    current_user: Usuario,
    db: Session
):
    # ADMIN / SUPERADMIN pueden gestionar cualquier servicio
    if current_user.rol in ["admin", "superadmin"]:
        return

    # NEGOCIO solo puede gestionar servicios de su propio negocio
    negocio = db.query(Negocio).filter(
        Negocio.id_usuario_propietario == current_user.id_usuario
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    if servicio.id_negocio != negocio.id_negocio:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para gestionar este servicio"
        )


# =========================
# CREAR SERVICIO
# =========================

@router.post("/", response_model=ServicioResponse, status_code=201)
def crear_servicio(
    request: Request,
    servicio: ServicioCreate,
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin", "superadmin"])
    ),
    db: Session = Depends(get_db)
):
    if servicio.duracion_minutos <= 0:
        raise HTTPException(
            status_code=400,
            detail="La duración del servicio debe ser mayor a 0 minutos"
        )

    if servicio.precio < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio del servicio no puede ser negativo"
        )

    # NEGOCIO: se asigna automáticamente a su negocio
    if current_user.rol == "negocio":
        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="No tienes un negocio registrado"
            )

        id_negocio = negocio.id_negocio

    # ADMIN / SUPERADMIN: deben enviar id_negocio
    else:
        if not servicio.id_negocio:
            raise HTTPException(
                status_code=400,
                detail="El administrador debe enviar id_negocio"
            )

        negocio = db.query(Negocio).filter(
            Negocio.id_negocio == servicio.id_negocio
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        id_negocio = servicio.id_negocio

    nuevo_servicio = Servicio(
        id_negocio=id_negocio,
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

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="SERVICIO_CREADO",
        modulo="servicios",
        tabla_afectada="core.servicios",
        id_registro=nuevo_servicio.id_servicio,
        detalle=(
            f"Usuario {current_user.correo} creó el servicio "
            f"{nuevo_servicio.nombre} para el negocio ID {nuevo_servicio.id_negocio}. "
            f"Duración: {nuevo_servicio.duracion_minutos} minutos. "
            f"Precio: {nuevo_servicio.precio}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    return nuevo_servicio


# =========================
# LISTAR SERVICIOS PÚBLICOS
# =========================

@router.get("/publicos", response_model=list[ServicioResponse])
def listar_servicios_publicos(
    db: Session = Depends(get_db)
):
    return db.query(Servicio).filter(
        Servicio.estado == "activo"
    ).all()


# =========================
# LISTAR SERVICIOS PÚBLICOS POR NEGOCIO
# =========================

@router.get("/publicos/negocio/{id_negocio}", response_model=list[ServicioResponse])
def listar_servicios_publicos_por_negocio(
    id_negocio: int,
    db: Session = Depends(get_db)
):
    return db.query(Servicio).filter(
        Servicio.id_negocio == id_negocio,
        Servicio.estado == "activo"
    ).all()


# =========================
# LISTAR SERVICIOS SEGÚN ROL
# =========================

@router.get("/", response_model=list[ServicioResponse])
def listar_servicios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "negocio", "admin", "superadmin"])
    )
):
    # ADMIN / SUPERADMIN ven todos
    if current_user.rol in ["admin", "superadmin"]:
        return db.query(Servicio).all()

    # NEGOCIO ve solo sus servicios
    if current_user.rol == "negocio":
        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio:
            raise HTTPException(
                status_code=404,
                detail="Negocio no encontrado"
            )

        return db.query(Servicio).filter(
            Servicio.id_negocio == negocio.id_negocio
        ).all()

    # CLIENTE ve servicios activos
    return db.query(Servicio).filter(
        Servicio.estado == "activo"
    ).all()


# =========================
# OBTENER SERVICIO
# =========================

@router.get("/{id_servicio}", response_model=ServicioResponse)
def obtener_servicio(
    id_servicio: int,
    db: Session = Depends(get_db)
):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if servicio.estado != "activo":
        raise HTTPException(
            status_code=404,
            detail="Servicio no disponible"
        )

    return servicio


# =========================
# ACTUALIZAR SERVICIO
# =========================

@router.put("/{id_servicio}", response_model=ServicioResponse)
def actualizar_servicio(
    request: Request,
    id_servicio: int,
    datos: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin", "superadmin"])
    )
):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    validar_acceso_servicio(
        servicio,
        current_user,
        db
    )

    update_data = datos.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar"
        )

    if "duracion_minutos" in update_data and update_data["duracion_minutos"] <= 0:
        raise HTTPException(
            status_code=400,
            detail="La duración del servicio debe ser mayor a 0 minutos"
        )

    if "precio" in update_data and update_data["precio"] < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio del servicio no puede ser negativo"
        )

    cambios = []

    for key, value in update_data.items():
        valor_anterior = getattr(servicio, key, None)

        if valor_anterior != value:
            cambios.append(f"{key}: {valor_anterior} -> {value}")

        setattr(servicio, key, value)

    db.commit()
    db.refresh(servicio)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="SERVICIO_ACTUALIZADO",
        modulo="servicios",
        tabla_afectada="core.servicios",
        id_registro=servicio.id_servicio,
        detalle=(
            f"Usuario {current_user.correo} actualizó el servicio "
            f"{servicio.nombre}. Cambios: {', '.join(cambios) if cambios else 'Sin cambios detectados'}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    return servicio


# =========================
# ELIMINAR / DESACTIVAR SERVICIO
# =========================

@router.delete("/{id_servicio}")
def eliminar_servicio(
    request: Request,
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["negocio", "admin", "superadmin"])
    )
):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    validar_acceso_servicio(
        servicio,
        current_user,
        db
    )

    servicio.estado = "inactivo"

    db.commit()

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="SERVICIO_ELIMINADO",
        modulo="servicios",
        tabla_afectada="core.servicios",
        id_registro=servicio.id_servicio,
        detalle=(
            f"Usuario {current_user.correo} desactivó/eliminó lógicamente "
            f"el servicio {servicio.nombre}."
        ),
        nivel="WARNING",
        resultado="OK"
    )

    return {
        "message": "Servicio eliminado correctamente"
    }