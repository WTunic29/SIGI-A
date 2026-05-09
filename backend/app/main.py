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

app = FastAPI(title="SIGI-A Backend")

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

@app.get("/")
def root():
    return {"message": "Backend SIGI-A funcionando correctamente"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()
    return {"database": "conectada", "resultado": value}
