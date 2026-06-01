from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date, time

from app.database import SessionLocal

from app.core.deps import (
    get_current_user,
    require_roles
)

from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.producto import Producto
from app.models.user import Usuario
from app.models.servicio import Servicio
from app.models.empleado import Empleado
from app.models.horario_empleado import HorarioEmpleado
from app.models.cita import Cita
from app.models.detalle_cita import DetalleCita


from app.schemas.carrito import (
    CarritoCreate,
    CarritoUpdate,
    CarritoResponse
)

from app.schemas.carrito_detalle import (
    AgregarProductoCarrito,
    AgregarCitaCarrito
)

router = APIRouter(
    prefix="/carritos",
    tags=["Carritos"]
)

from app.utils.auditoria import registrar_auditoria

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VALIDAR ACCESO CARRITO
# =========================

def validar_acceso_carrito(
    carrito: Carrito,
    current_user: Usuario
):

    # ADMIN
    if current_user.rol == "admin":
        return

    # CLIENTE
    if carrito.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )

# =========================
# HELPERS CARRITO
# =========================

def obtener_carrito_activo_usuario(
    db: Session,
    id_usuario: int
):
    return db.query(Carrito).filter(
        Carrito.id_usuario == id_usuario,
        Carrito.estado == "activo"
    ).order_by(
        Carrito.id_carrito.desc()
    ).first()


def recalcular_total_carrito(
    db: Session,
    carrito: Carrito
):
    detalles = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    total = sum([
        detalle.subtotal or 0
        for detalle in detalles
    ])

    carrito.total_estimado = total
    carrito.fecha_actualizacion = datetime.utcnow()
    return total

def liberar_reservas_vencidas(db: Session):
    ahora = datetime.utcnow()

    detalles_vencidos = db.query(CarritoDetalle).filter(
        CarritoDetalle.estado_reserva == "RESERVADO",
        CarritoDetalle.fecha_expiracion_reserva < ahora
    ).all()

    carritos_afectados = set()

    for detalle in detalles_vencidos:
        detalle.estado_reserva = "VENCIDO"
        carritos_afectados.add(detalle.id_carrito)

        if detalle.id_cita:
            cita = db.query(Cita).filter(
                Cita.id_cita == detalle.id_cita,
                Cita.estado == "reservada_carrito"
            ).first()

            if cita:
                cita.estado = "vencida"

    for id_carrito in carritos_afectados:
        carrito = db.query(Carrito).filter(
            Carrito.id_carrito == id_carrito
        ).first()

        if carrito:
            recalcular_total_carrito(db, carrito)

    return len(detalles_vencidos)


def obtener_stock_disponible_producto(
    db: Session,
    producto: Producto
):
    cantidad_reservada = db.query(
        func.coalesce(func.sum(CarritoDetalle.cantidad), 0)
    ).filter(
        CarritoDetalle.id_producto == producto.id_producto,
        CarritoDetalle.estado_reserva == "RESERVADO",
        CarritoDetalle.fecha_expiracion_reserva > datetime.utcnow()
    ).scalar()

    return producto.stock - cantidad_reservada

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


def horario_ocupado_cita(
    db: Session,
    id_empleado: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time
) -> bool:
    estados_libres = ["cancelada", "anulada", "eliminada", "rechazada", "vencida"]

    citas = db.query(Cita).filter(
        Cita.id_empleado == id_empleado,
        Cita.fecha == fecha,
        ~Cita.estado.in_(estados_libres)
    ).all()

    nuevo_inicio = combinar_fecha_hora(fecha, hora_inicio)
    nuevo_fin = combinar_fecha_hora(fecha, hora_fin)

    for cita in citas:
        cita_inicio = combinar_fecha_hora(fecha, cita.hora_inicio)
        cita_fin = combinar_fecha_hora(fecha, cita.hora_fin)

        if se_cruza(nuevo_inicio, nuevo_fin, cita_inicio, cita_fin):
            return True

    return False


def parse_fecha_hora_cita(fecha_str: str, hora_str: str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_str, "%H:%M:%S").time()
        return fecha, hora_inicio
    except ValueError:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_inicio = datetime.strptime(hora_str, "%H:%M").time()
            return fecha, hora_inicio
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha u hora inválido. Usa fecha YYYY-MM-DD y hora HH:MM o HH:MM:SS."
            )

    cantidad_reservada = db.query(
        func.coalesce(func.sum(CarritoDetalle.cantidad), 0)
    ).filter(
        CarritoDetalle.id_producto == producto.id_producto,
        CarritoDetalle.estado_reserva == "RESERVADO",
        CarritoDetalle.fecha_expiracion_reserva > datetime.utcnow()
    ).scalar()

    return producto.stock - cantidad_reservada

# =========================
# OBTENER CARRITO ACTIVO
# =========================

@router.get("/activo", response_model=CarritoResponse | None)
def obtener_carrito_activo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)
    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        return None
    db.flush()
    recalcular_total_carrito(db, carrito)
    db.commit()
    db.refresh(carrito)

    return carrito

# =========================
# OBTENER CARRITO ACTIVO CON DETALLE
# =========================

@router.get("/activo/detalle")
def obtener_carrito_activo_detalle(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)

    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        return {
            "carrito": None,
            "items": []
        }

    recalcular_total_carrito(db, carrito)
    db.commit()
    db.refresh(carrito)

    detalles = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    items = []

    for detalle in detalles:
        item = {
            "id_carrito_detalle": detalle.id_carrito_detalle,
            "id_carrito": detalle.id_carrito,
            "tipo_item": detalle.tipo_item,
            "id_producto": detalle.id_producto,
            "id_servicio": detalle.id_servicio,
            "id_cita": detalle.id_cita,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal,
            "estado_reserva": detalle.estado_reserva,
            "fecha_reserva": detalle.fecha_reserva,
            "fecha_expiracion_reserva": detalle.fecha_expiracion_reserva
        }

        if detalle.tipo_item == "producto" and detalle.id_producto:
            producto = db.query(Producto).filter(
                Producto.id_producto == detalle.id_producto
            ).first()

            item.update({
                "nombre": producto.nombre if producto else "Producto no disponible",
                "descripcion": producto.descripcion if producto else None,
                "imagen_url": producto.imagen_url if producto else None
            })

        elif detalle.tipo_item == "servicio" and detalle.id_servicio:
            servicio = db.query(Servicio).filter(
                Servicio.id_servicio == detalle.id_servicio
            ).first()

            cita = None
            empleado = None

            if detalle.id_cita:
                cita = db.query(Cita).filter(
                    Cita.id_cita == detalle.id_cita
                ).first()

                if cita:
                    empleado = db.query(Empleado).filter(
                        Empleado.id_empleado == cita.id_empleado
                    ).first()

            item.update({
                "nombre": servicio.nombre if servicio else "Servicio no disponible",
                "descripcion": servicio.descripcion if servicio else None,
                "imagen_url": servicio.imagen_url if servicio else None,
                "id_cita": detalle.id_cita,
                "fecha": cita.fecha if cita else None,
                "hora_inicio": cita.hora_inicio if cita else None,
                "hora_fin": cita.hora_fin if cita else None,
                "estado_cita": cita.estado if cita else None,
                "id_empleado": cita.id_empleado if cita else None,
                "empleado_nombre": empleado.nombre if empleado else None,
                "empleado_apellido": empleado.apellido if empleado else None
            })

        else:
            item.update({
                "nombre": "Item no disponible",
                "descripcion": None,
                "imagen_url": None
            })

        items.append(item)

    return {
        "carrito": carrito,
        "items": items
    }

# =========================
# AGREGAR PRODUCTO AL CARRITO
# =========================

@router.post("/agregar-producto", response_model=CarritoResponse)
def agregar_producto_carrito(
    request: Request,
    datos: AgregarProductoCarrito,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):
    liberar_reservas_vencidas(db)
    if datos.cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor a cero"
        )

    producto = db.query(Producto).filter(
        Producto.id_producto == datos.id_producto,
        Producto.estado == "activo"
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o inactivo"
        )

    stock_disponible = obtener_stock_disponible_producto(
        db,
        producto
    )

    if stock_disponible < datos.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible actualmente: {stock_disponible}"
        )  

    ahora = datetime.utcnow()
    expiracion = ahora + timedelta(minutes=15)

    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        carrito = Carrito(
            id_usuario=current_user.id_usuario,
            id_negocio=producto.id_negocio,
            estado="activo",
            fecha_creacion=ahora,
            fecha_expiracion=expiracion,
            fecha_actualizacion=ahora,
            total_estimado=0
        )
        db.add(carrito)
        db.flush()
    else:
        if carrito.id_negocio and carrito.id_negocio != producto.id_negocio:
            raise HTTPException(
                status_code=400,
                detail="No puedes mezclar productos de diferentes negocios en el mismo carrito"
            )

        carrito.id_negocio = producto.id_negocio
        carrito.fecha_expiracion = expiracion
        carrito.fecha_actualizacion = ahora

    subtotal = producto.precio * datos.cantidad

    detalle_existente = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.id_producto == producto.id_producto,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).first()

    if detalle_existente:
        nueva_cantidad = detalle_existente.cantidad + datos.cantidad

        cantidad_actual_en_carrito = detalle_existente.cantidad or 0
        stock_disponible_real = stock_disponible + cantidad_actual_en_carrito

        if stock_disponible_real < nueva_cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para aumentar la cantidad. Disponible actualmente: {stock_disponible_real}"
            )

        detalle_existente.cantidad = nueva_cantidad
        detalle_existente.precio_unitario = producto.precio
        detalle_existente.subtotal = producto.precio * nueva_cantidad
        detalle_existente.fecha_reserva = ahora
        detalle_existente.fecha_expiracion_reserva = expiracion
    else:
        detalle = CarritoDetalle(
            id_carrito=carrito.id_carrito,
            tipo_item="producto",
            id_producto=producto.id_producto,
            id_servicio=None,
            cantidad=datos.cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal,
            estado_reserva="RESERVADO",
            fecha_reserva=ahora,
            fecha_expiracion_reserva=expiracion
        )
        db.add(detalle)
    db.flush()
    recalcular_total_carrito(db, carrito)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="ITEM_AGREGADO_CARRITO",
        modulo="carritos",
        tabla_afectada="core.carrito_detalle",
        id_registro=carrito.id_carrito,
        detalle=(
            f"Usuario {current_user.correo} agregó producto ID "
            f"{producto.id_producto} al carrito por cantidad {datos.cantidad}. "
            f"Reserva válida hasta {expiracion}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    db.commit()
    db.refresh(carrito)

    return carrito

# =========================
# AGREGAR CITA AL CARRITO
# =========================

@router.post("/agregar-cita", response_model=CarritoResponse)
def agregar_cita_carrito(
    request: Request,
    datos: AgregarCitaCarrito,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):
    liberar_reservas_vencidas(db)

    fecha_cita, hora_inicio = parse_fecha_hora_cita(
        datos.fecha,
        datos.hora_inicio
    )

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == datos.id_empleado,
        Empleado.estado == "activo"
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado o inactivo"
        )

    if empleado.id_negocio != datos.id_negocio:
        raise HTTPException(
            status_code=400,
            detail="El empleado no pertenece al negocio seleccionado"
        )

    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == datos.id_servicio,
        Servicio.estado == "activo"
    ).first()

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado o inactivo"
        )

    if servicio.id_negocio != datos.id_negocio:
        raise HTTPException(
            status_code=400,
            detail="El servicio no pertenece al negocio seleccionado"
        )

    hora_fin = calcular_hora_fin(
        fecha_cita,
        hora_inicio,
        servicio.duracion_minutos
    )

    if not empleado_trabaja_en_bloque(
        db,
        datos.id_empleado,
        fecha_cita,
        hora_inicio,
        hora_fin
    ):
        raise HTTPException(
            status_code=400,
            detail="El empleado no trabaja en ese horario"
        )

    if horario_ocupado_cita(
        db,
        datos.id_empleado,
        fecha_cita,
        hora_inicio,
        hora_fin
    ):
        raise HTTPException(
            status_code=400,
            detail="Ese horario ya no está disponible. Selecciona otra hora."
        )

    ahora = datetime.utcnow()
    expiracion = ahora + timedelta(minutes=15)

    carrito = obtener_carrito_activo_usuario(
        db,
        current_user.id_usuario
    )

    if not carrito:
        carrito = Carrito(
            id_usuario=current_user.id_usuario,
            id_negocio=datos.id_negocio,
            estado="activo",
            fecha_creacion=ahora,
            fecha_expiracion=expiracion,
            fecha_actualizacion=ahora,
            total_estimado=0
        )
        db.add(carrito)
        db.flush()
    else:
        if carrito.id_negocio and carrito.id_negocio != datos.id_negocio:
            raise HTTPException(
                status_code=400,
                detail="No puedes mezclar servicios de diferentes negocios en el mismo carrito"
            )

        carrito.id_negocio = datos.id_negocio
        carrito.fecha_expiracion = expiracion
        carrito.fecha_actualizacion = ahora

    nueva_cita = Cita(
        id_cliente=current_user.id_usuario,
        id_negocio=datos.id_negocio,
        id_empleado=datos.id_empleado,
        fecha=fecha_cita,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado="reservada_carrito",
        observaciones=datos.observaciones
    )

    db.add(nueva_cita)
    db.flush()

    nuevo_detalle_cita = DetalleCita(
        id_cita=nueva_cita.id_cita,
        id_servicio=servicio.id_servicio,
        precio=servicio.precio,
        duracion=servicio.duracion_minutos
    )

    db.add(nuevo_detalle_cita)

    detalle_carrito = CarritoDetalle(
        id_carrito=carrito.id_carrito,
        tipo_item="servicio",
        id_producto=None,
        id_servicio=servicio.id_servicio,
        id_cita=nueva_cita.id_cita,
        cantidad=1,
        precio_unitario=servicio.precio,
        subtotal=servicio.precio,
        estado_reserva="RESERVADO",
        fecha_reserva=ahora,
        fecha_expiracion_reserva=expiracion
    )

    db.add(detalle_carrito)
    db.flush()

    recalcular_total_carrito(db, carrito)

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CITA_AGREGADA_CARRITO",
        modulo="carritos",
        tabla_afectada="core.carrito_detalle",
        id_registro=carrito.id_carrito,
        detalle=(
            f"Usuario {current_user.correo} reservó cita ID {nueva_cita.id_cita} "
            f"para servicio ID {servicio.id_servicio}, empleado ID {empleado.id_empleado}, "
            f"fecha {fecha_cita}, hora {hora_inicio} - {hora_fin}. "
            f"Reserva válida hasta {expiracion}."
        ),
        nivel="INFO",
        resultado="OK"
    )

    db.commit()
    db.refresh(carrito)

    return carrito

# =========================
# CONVERTIR CARRITO A PEDIDO
# =========================

@router.post("/{id_carrito}/convertir")
def convertir_carrito_a_pedido(
    id_carrito: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):
    liberar_reservas_vencidas(db)

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    if carrito.estado != "activo":
        raise HTTPException(
            status_code=400,
            detail="El carrito ya no está activo"
        )

    detalles_reservados = db.query(CarritoDetalle).filter(
        CarritoDetalle.id_carrito == carrito.id_carrito,
        CarritoDetalle.estado_reserva == "RESERVADO"
    ).all()

    if not detalles_reservados:
        raise HTTPException(
            status_code=400,
            detail="El carrito no tiene reservas activas"
        )

    for detalle in detalles_reservados:
        detalle.estado_reserva = "CONVERTIDO"

        if detalle.id_cita:
            cita = db.query(Cita).filter(
                Cita.id_cita == detalle.id_cita
            ).first()

            if cita and cita.estado == "reservada_carrito":
                cita.estado = "pendiente_pago"

    carrito.estado = "cerrado"
    carrito.fecha_actualizacion = datetime.utcnow()

    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="CARRITO_CONVERTIDO_PEDIDO",
        modulo="carritos",
        tabla_afectada="core.carritos",
        id_registro=carrito.id_carrito,
        detalle=(
            f"Usuario {current_user.correo} convirtió el carrito "
            f"ID {carrito.id_carrito} en pedido."
        ),
        nivel="INFO",
        resultado="OK"
    )

    db.commit()
    db.refresh(carrito)

    return {
        "message": "Carrito cerrado correctamente después de crear el pedido",
        "id_carrito": carrito.id_carrito,
        "estado": carrito.estado
    }

# =========================
# CREAR CARRITO
# =========================

@router.post("/", response_model=CarritoResponse)
def crear_carrito(
    carrito: CarritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente"])
    )
):

    nuevo = Carrito(
        id_usuario=current_user.id_usuario,
        estado=carrito.estado,
        fecha_creacion=datetime.utcnow()
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# =========================
# LISTAR CARRITOS
# =========================

@router.get("/", response_model=list[CarritoResponse])
def listar_carritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    # ADMIN
    if current_user.rol == "admin":
        return db.query(Carrito).all()

    # CLIENTE
    return db.query(Carrito).filter(
        Carrito.id_usuario == current_user.id_usuario
    ).all()


# =========================
# OBTENER CARRITO
# =========================

@router.get("/{id_carrito}", response_model=CarritoResponse)
def obtener_carrito(
    id_carrito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    return carrito


# =========================
# ACTUALIZAR CARRITO
# =========================

@router.put("/{id_carrito}", response_model=CarritoResponse)
def actualizar_carrito(
    id_carrito: int,
    datos: CarritoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    update_data = datos.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(carrito, key, value)

    db.commit()
    db.refresh(carrito)

    return carrito


# =========================
# ELIMINAR CARRITO
# =========================

@router.delete("/{id_carrito}")
def eliminar_carrito(
    id_carrito: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles(["cliente", "admin"])
    )
):

    carrito = db.query(Carrito).filter(
        Carrito.id_carrito == id_carrito
    ).first()

    if not carrito:
        raise HTTPException(
            status_code=404,
            detail="Carrito no encontrado"
        )

    validar_acceso_carrito(
        carrito,
        current_user
    )

    db.delete(carrito)
    db.commit()

    return {
        "message": "Carrito eliminado"
    }
