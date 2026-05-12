import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt

from app.utils.security import SECRET_KEY, ALGORITHM, hash_password

# Base de datos simplificada para testing
from sqlalchemy.ext.declarative import declarative_base
TestBase = declarative_base()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)

# Crear tablas de prueba
TestBase.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    """Fixture para cliente de prueba sin importar app completo"""
    from fastapi import FastAPI
    app = FastAPI()
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Fixture para generar headers de autenticación"""
    def create_headers(email: str, rol: str = "cliente"):
        # Crear token de prueba
        payload = {
            "sub": email,
            "rol": rol,
            "exp": 9999999999  # Token que no expira
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"Authorization": f"Bearer {token}"}
    return create_headers

@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos de prueba"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
