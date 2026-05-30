from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine
from app.routes import user
from app.routes import negocio
from app.routes import servicio
from app.routes import empleado
from app.routes import empleado_servicio
from app.routes import horario_empleado
from app.routes import cita
from app.routes import calificacion
from app.routes import producto
from app.routes import inventario_movimiento
from app.routes import notificacion
from app.routes.pago import router as pago_router
from app.routes.pedido import router as pedido_router
from app.routes import pedido_detalle
from app.routes import carrito
from app.routes import carrito_detalle
from app.routes import factura
from app.routes import favorito
from app.routes import token_recuperacion
from app.routes import sesion
from app.routes import auditoria
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler
from app.middleware.security_logs import SecurityLogsMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.core.logging_config import *
import os

from app.core.rate_limit import limiter

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="SIGI-A Backend",

    docs_url=None if ENVIRONMENT == "production" else "/docs",

    redoc_url=None if ENVIRONMENT == "production" else "/redoc",

    openapi_url=None if ENVIRONMENT == "production" else "/openapi.json"
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)

app.add_middleware(SecurityLogsMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(negocio.router, prefix="/negocios", tags=["Negocios"])
app.include_router(user.router, prefix="/auth", tags=["Auth"])
app.include_router(servicio.router, prefix="/servicios", tags=["Servicios"])
app.include_router(empleado.router, prefix="/empleados", tags=["Empleados"])
app.include_router(
    empleado_servicio.router,
    prefix="/empleado-servicio",
    tags=["Empleado Servicio"]
)
app.include_router(
    horario_empleado.router,
    prefix="/horarios-empleado",
    tags=["Horarios Empleado"]
)
app.include_router(cita.router, prefix="/citas", tags=["Citas"])
app.include_router(
    calificacion.router,
    prefix="/calificaciones",
    tags=["Calificaciones"]
)

app.include_router(
    producto.router,
    prefix="/productos",
    tags=["Productos"]
)

app.include_router(
    inventario_movimiento.router,
    prefix="/inventario-movimientos",
    tags=["Inventario"]
)

app.include_router(
    notificacion.router,
    prefix="/notificaciones",
    tags=["Notificaciones"]
)
app.include_router(pago_router)
app.include_router(pedido_router)
app.include_router(pedido_detalle.router)
app.include_router(carrito.router)
app.include_router(carrito_detalle.router)
app.include_router(factura.router)
app.include_router(favorito.router)
app.include_router(token_recuperacion.router)
app.include_router(sesion.router)
app.include_router(auditoria.router)

@app.get("/")
def root():
    return {"message": "Backend SIGI-A funcionando correctamente"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()
    return {"database": "conectada", "resultado": value}
