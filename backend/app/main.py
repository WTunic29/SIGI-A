from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app.routes import user

app = FastAPI(title="SIGI-A Backend")

app.include_router(user.router, prefix="/users")


@app.get("/")
def root():
    return {"message": "Backend SIGI-A funcionando correctamente"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()
    return {"database": "conectada", "resultado": value}