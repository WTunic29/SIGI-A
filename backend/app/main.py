from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine
from app.routes import user
from app.routes import negocio

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


@app.get("/")
def root():
    return {"message": "Backend SIGI-A funcionando correctamente"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()
    return {"database": "conectada", "resultado": value}
