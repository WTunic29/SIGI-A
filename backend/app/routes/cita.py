from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from app.database import get_db
from app.core.deps import require_roles

from app.models.user import Usuario
from app.models.negocio import Negocio
from app.models.empleado import Empleado
from app.models.servicio import Servicio
from app.models.horario_empleado import HorarioEmpleado
from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita

from app.schemas.cita import (
    CitaCreate,
    CitaUpdate,
    CitaResponse,
    DetalleCitaCreate,
    DetalleCitaResponse
)

from app.utils.auditoria import registrar_auditoria

router = APIRouter()


# =========================
# HELPERS
# =========================

ESTADOS_CANCELADOS = ["cancelada", "anulada", "eliminada", "rechazada"]


def obtener_negocio_usuario(db: Session, id_usuario: int, id_negocio: int):
    return db.query(Negocio).filter(
        Negocio.id_usuario_propietario == id_usuario,
        Negocio.id_negocio == id_negocio
    ).first()


def combinar_fecha_hora(fecha: date, hora: time) -> datetime:
    return datetime.combine(fecha, hora)


def calcular_hora_fin(fecha: date, hora_inicio: time, duracion_minutos: int) -> time:
    inicio_dt = combinar_fecha_hora(fecha, hora_inicio)
    fin_dt = inicio_dt + timedelta(minutes=duracion_minutos)
    return fin_dt.time()


def se_cruza(inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime) -> bool:
    return inicio_a < fin_b and fin_a > inicio_b


def empleado_trabaja_en_bloque(
    db: Session,
    id_empleado: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time
) -> bool:
    # Soporta dos convenciones:
    # Python weekday: lunes=0 domingo=6
    # ISO weekday: lunes=1 domingo=7
    dias_posibles = [fecha.weekday(), fecha.isoweekday()]

    horarios = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_empleado == id_empleado,
        HorarioEmpleado.dia_semana.in_(dias_posibles),
        HorarioEmpleado.disponible == True
    ).all()

    inicio_dt = combinar_fecha_hora(fecha, hora_inicio)
    fin_dt = combinar_fecha_hora(fecha, hora_fin)

    for horario in horarios:
        laboral_inicio = combinar_fecha_hora(fecha, horario.hora_inicio)
        laboral_fin = combinar_fecha_hora(fecha, horario.hora_fin)

        if inicio_dt >= laboral_inicio and fin_dt <= laboral_fin:
            return True

    return False


def horario_ocupado(
    db: Session,
    id_empleado: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    id_cita_ignorar: Optional[int] = None
) -> bool:
    query = db.query(Cita).filter(
        Cita.id_empleado == id_empleado,
        Cita.fecha == fecha,
        ~Cita.estado.in_(ESTADOS_CANCELADOS)
    )

    if id_cita_ignorar:
        query = query.filter(Cita.id_cita != id_cita_ignorar)

    citas = query.all()

    nuevo_inicio = combinar_fecha_hora(fecha, hora_inicio)
    nuevo_fin = combinar_fecha_hora(fecha, hora_fin)

    for cita in citas:
        cita_inicio = combinar_fecha_hora(fecha, cita.hora_inicio)
        cita_fin = combinar_fecha_hora(fecha, cita.hora_fin)

        if se_cruza(nuevo_inicio, nuevo_fin, cita_inicio, cita_fin):
            return True

    return False


def validar_disponibilidad_cita(
    db: Session,
    id_empleado: int,
    id_servicio: int,
    id_negocio: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: Optional[time] = None,
    id_cita_ignorar: Optional[int] = None
):
    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado,
        Empleado.estado == "activo"
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado o inactivo"
        )

    if empleado.id_negocio != id_negocio:
        raise HTTPException(
            status_code=400,
            detail="El empleado no pertenece al negocio seleccionado"
        )

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio,
        Servicio.estado == "activo"
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado o inactivo"
        )

    if servicio.id_negocio != id_negocio:
        raise HTTPException(
            status_code=400,
            detail="El servicio no pertenece al negocio seleccionado"
        )

    hora_fin_calculada = calcular_hora_fin(
        fecha,
        hora_inicio,
        servicio.duracion_minutos
    )

    if hora_fin and hora_fin != hora_fin_calculada:
        raise HTTPException(
            status_code=400,
            detail="La duración no corresponde al servicio seleccionado"
        )

    if not empleado_trabaja_en_bloque(
        db,
        id_empleado,
        fecha,
        hora_inicio,
        hora_fin_calculada
    ):
        raise HTTPException(
            status_code=400,
            detail="El empleado no trabaja en ese horario"
        )

    if horario_ocupado(
        db,
        id_empleado,
        fecha,
        hora_inicio,
        hora_fin_calculada,
        id_cita_ignorar=id_cita_ignorar
    ):
        raise HTTPException(
            status_code=400,
            detail="Ese horario ya no está disponible. Selecciona otra hora."
        )

    return servicio, hora_fin_calculada


def calcular_bloques_disponibles(
    db: Session,
    id_empleado: int,
    id_servicio: int,
    fecha: date
):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio,
        Servicio.estado == "activo"
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado o inactivo"
        )

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado,
        Empleado.estado == "activo"
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado o inactivo"
        )

    if empleado.id_negocio != servicio.id_negocio:
        raise HTTPException(
            status_code=400,
            detail="El empleado no pertenece al negocio del servicio"
        )

    dias_posibles = [fecha.weekday(), fecha.isoweekday()]

    horarios_laborales = db.query(HorarioEmpleado).filter(
        HorarioEmpleado.id_empleado == id_empleado,
        HorarioEmpleado.dia_semana.in_(dias_posibles),
        HorarioEmpleado.disponible == True
    ).all()

    if not horarios_laborales:
        return {
            "fecha": str(fecha),
            "id_empleado": id_empleado,
            "id_servicio": id_servicio,
            "duracion_minutos": servicio.duracion_minutos,
            "horarios_disponibles": []
        }

    citas_existentes = db.query(Cita).filter(
        Cita.id_empleado == id_empleado,
        Cita.fecha == fecha,
        ~Cita.estado.in_(ESTADOS_CANCELADOS)
    ).all()

    bloques = []
    duracion = timedelta(minutes=servicio.duracion_minutos)

    for horario in horarios_laborales:
        cursor = combinar_fecha_hora(fecha, horario.hora_inicio)
        fin_jornada = combinar_fecha_hora(fecha, horario.hora_fin)

        while cursor + duracion <= fin_jornada:
            bloque_inicio = cursor
            bloque_fin = cursor + duracion

            ocupado = False

            for cita in citas_existentes:
                cita_inicio = combinar_fecha_hora(fecha, cita.hora_inicio)
                cita_fin = combinar_fecha_hora(fecha, cita.hora_fin)

                if se_cruza(bloque_inicio, bloque_fin, cita_inicio, cita_fin):
                    ocupado = True
                    break

            if not ocupado:
                bloques.append({
                    "hora_inicio": bloque_inicio.time().strftime("%H:%M:%S"),
                    "hora_fin": bloque_fin.time().strftime("%H:%M:%S")
                })

            cursor = bloque_fin

    return {
        "fecha": str(fecha),
        "id_empleado": id_empleado,
        "id_servicio": id_servicio,
        "duracion_minutos": servicio.duracion_minutos,
        "horarios_disponibles": bloques
    }


# =========================
# DISPONIBILIDAD DE CITAS
# =========================

@router.get("/disponibilidad")
def obtener_disponibilidad(
    fecha: date,
    id_servicio: int,
    id_empleado: Optional[int] = Query(default=None),
    id_trabajador: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    empleado_final = id_empleado or id_trabajador

    if not empleado_final:
        raise HTTPException(
            status_code=400,
            detail="Debes enviar id_empleado o id_trabajador"
        )

    return calcular_bloques_disponibles(
        db=db,
        id_empleado=empleado_final,
        id_servicio=id_servicio,
        fecha=fecha
    )


# =========================
# CREAR CITA
# =========================

@router.post("/", response_model=CitaResponse)
def crear_cita(
    request: Request,
    cita: CitaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "admin", "superadmin"]))
):
    servicio, hora_fin_calculada = validar_disponibilidad_cita(
        db=db,
        id_empleado=cita.id_empleado,
        id_servicio=cita.id_servicio,
        id_negocio=cita.id_negocio,
        fecha=cita.fecha,
        hora_inicio=cita.hora_inicio,
        hora_fin=cita.hora_fin
    )

    id_cliente = current_user.id_usuario

    if current_user.rol in ["admin", "superadmin"] and cita.id_cliente:
        id_cliente = cita.id_cliente

    nueva_cita = Cita(
        id_cliente=id_cliente,
        id_negocio=cita.id_negocio,
        id_empleado=cita.id_empleado,
        fecha=cita.fecha,
        hora_inicio=cita.hora_inicio,
        hora_fin=hora_fin_calculada,
        estado="pendiente",
        observaciones=cita.observaciones
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)

    nuevo_detalle = DetalleCita(
        id_cita=nueva_cita.id_cita,
        id_servicio=cita.id_servicio,
        precio=servicio.precio,
        duracion=servicio.duracion_minutos
    )

    db.add(nuevo_detalle)
    db.commit()

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CITA_CREADA",
        modulo="citas",
        tabla_afectada="core.citas",
        id_registro=nueva_cita.id_cita,
        detalle=(
            f"Usuario {current_user.correo} creó cita para empleado ID {cita.id_empleado}, "
            f"servicio ID {cita.id_servicio}, fecha {cita.fecha}, "
            f"hora {cita.hora_inicio} - {hora_fin_calculada}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    return nueva_cita


# =========================
# LISTAR TODAS LAS CITAS - ADMIN / SUPERADMIN
# =========================

@router.get("/")
def listar_citas_admin(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["admin", "superadmin"]))
):
    resultados = (
        db.query(
            Cita,
            Usuario.nombre.label("cliente_nombre"),
            Usuario.apellido.label("cliente_apellido"),
            Usuario.correo.label("cliente_correo"),
            Negocio.nombre_negocio.label("negocio_nombre"),
            Empleado.nombre.label("empleado_nombre"),
            Empleado.apellido.label("empleado_apellido"),
            Servicio.nombre.label("servicio_nombre")
        )
        .join(Usuario, Usuario.id_usuario == Cita.id_cliente)
        .join(Negocio, Negocio.id_negocio == Cita.id_negocio)
        .join(Empleado, Empleado.id_empleado == Cita.id_empleado)
        .outerjoin(DetalleCita, DetalleCita.id_cita == Cita.id_cita)
        .outerjoin(Servicio, Servicio.id_servicio == DetalleCita.id_servicio)
        .order_by(Cita.fecha.desc(), Cita.hora_inicio.desc())
        .all()
    )

    citas = []

    for cita, cliente_nombre, cliente_apellido, cliente_correo, negocio_nombre, empleado_nombre, empleado_apellido, servicio_nombre in resultados:
        citas.append({
            "id_cita": cita.id_cita,
            "id_cliente": cita.id_cliente,
            "id_negocio": cita.id_negocio,
            "id_empleado": cita.id_empleado,
            "fecha": cita.fecha,
            "hora_inicio": cita.hora_inicio,
            "hora_fin": cita.hora_fin,
            "estado": cita.estado,
            "observaciones": cita.observaciones,
            "fecha_creacion": cita.fecha_creacion,
            "cliente_nombre": cliente_nombre,
            "cliente_apellido": cliente_apellido,
            "cliente_correo": cliente_correo,
            "negocio_nombre": negocio_nombre,
            "empleado_nombre": empleado_nombre,
            "empleado_apellido": empleado_apellido,
            "servicio_nombre": servicio_nombre
        })

    return citas



# =========================
# LISTAR CITAS POR NEGOCIO
# =========================

@router.get("/negocio/{id_negocio}")
def listar_citas_negocio(
    id_negocio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin", "superadmin"]))
):
    if current_user.rol == "negocio":
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

    resultados = (
        db.query(
            Cita,
            Usuario.nombre.label("cliente_nombre"),
            Usuario.apellido.label("cliente_apellido"),
            Usuario.correo.label("cliente_correo"),
            Empleado.nombre.label("empleado_nombre"),
            Empleado.apellido.label("empleado_apellido"),
            Servicio.nombre.label("servicio_nombre")
        )
        .join(Usuario, Usuario.id_usuario == Cita.id_cliente)
        .join(Empleado, Empleado.id_empleado == Cita.id_empleado)
        .outerjoin(DetalleCita, DetalleCita.id_cita == Cita.id_cita)
        .outerjoin(Servicio, Servicio.id_servicio == DetalleCita.id_servicio)
        .filter(Cita.id_negocio == id_negocio)
        .order_by(Cita.fecha.asc(), Cita.hora_inicio.asc())
        .all()
    )

    citas = []

    for cita, cliente_nombre, cliente_apellido, cliente_correo, empleado_nombre, empleado_apellido, servicio_nombre in resultados:
        citas.append({
            "id_cita": cita.id_cita,
            "id_cliente": cita.id_cliente,
            "id_negocio": cita.id_negocio,
            "id_empleado": cita.id_empleado,
            "fecha": cita.fecha,
            "hora_inicio": cita.hora_inicio,
            "hora_fin": cita.hora_fin,
            "estado": cita.estado,
            "observaciones": cita.observaciones,
            "fecha_creacion": cita.fecha_creacion,
            "cliente_nombre": cliente_nombre,
            "cliente_apellido": cliente_apellido,
            "cliente_correo": cliente_correo,
            "empleado_nombre": empleado_nombre,
            "empleado_apellido": empleado_apellido,
            "servicio_nombre": servicio_nombre
        })

    return citas


# =========================
# LISTAR CITAS POR EMPLEADO
# =========================

@router.get("/empleado/{id_empleado}", response_model=List[CitaResponse])
def listar_citas_empleado(
    id_empleado: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin", "superadmin"]))
):
    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    if current_user.rol == "negocio":
        negocio = db.query(Negocio).filter(
            Negocio.id_usuario_propietario == current_user.id_usuario
        ).first()

        if not negocio or empleado.id_negocio != negocio.id_negocio:
            raise HTTPException(
                status_code=403,
                detail="No puedes ver citas de este empleado"
            )

    return db.query(Cita).filter(
        Cita.id_empleado == id_empleado
    ).all()


# =========================
# LISTAR CITAS POR CLIENTE
# =========================

@router.get("/cliente/{id_cliente}", response_model=List[CitaResponse])
def listar_citas_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin", "superadmin"]))
):
    if current_user.rol == "cliente" and id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver citas de otro cliente"
        )

    return db.query(Cita).filter(
        Cita.id_cliente == id_cliente
    ).all()


# =========================
# ACTUALIZAR CITA
# =========================

@router.put("/{id_cita}", response_model=CitaResponse)
def actualizar_cita(
    request: Request,
    id_cita: int,
    cita: CitaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["negocio", "admin", "superadmin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
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
                detail="No puedes modificar esta cita"
            )

    datos = cita.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(cita_db, campo, valor)

    db.commit()
    db.refresh(cita_db)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CITA_ACTUALIZADA",
        modulo="citas",
        tabla_afectada="core.citas",
        id_registro=cita_db.id_cita,
        detalle=f"Usuario {current_user.correo} actualizó la cita ID {cita_db.id_cita}.",
        nivel="INFO",
        resultado="OK"
    )

    return cita_db


# =========================
# CANCELAR CITA
# =========================

@router.delete("/{id_cita}")
def cancelar_cita(
    request: Request,
    id_cita: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin", "superadmin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente" and cita_db.id_cliente != current_user.id_usuario:
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

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CITA_CANCELADA",
        modulo="citas",
        tabla_afectada="core.citas",
        id_registro=cita_db.id_cita,
        detalle=f"Usuario {current_user.correo} canceló la cita ID {cita_db.id_cita}.",
        nivel="WARNING",
        resultado="OK"
    )

    return {"message": "Cita cancelada correctamente"}


# =========================
# AGREGAR DETALLE CITA
# =========================

@router.post("/{id_cita}/detalle", response_model=DetalleCitaResponse)
def agregar_detalle_cita(
    id_cita: int,
    detalle: DetalleCitaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin", "superadmin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente" and cita_db.id_cliente != current_user.id_usuario:
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


# =========================
# LISTAR DETALLE CITA
# =========================

@router.get("/{id_cita}/detalle", response_model=List[DetalleCitaResponse])
def listar_detalle_cita(
    id_cita: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["cliente", "negocio", "admin", "superadmin"]))
):
    cita_db = db.query(Cita).filter(
        Cita.id_cita == id_cita
    ).first()

    if not cita_db:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )

    if current_user.rol == "cliente" and cita_db.id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No puedes ver este detalle"
        )

    return db.query(DetalleCita).filter(
        DetalleCita.id_cita == id_cita
    ).all()