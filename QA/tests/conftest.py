"""
Configuración de pytest: SQLite en memoria (sin tocar database.py del backend)
y autenticación sin tabla `sesion` (misma semántica que JWT + usuario en BD).
"""

from __future__ import annotations

import importlib
import os
from typing import Generator

import sqlalchemy

_original_create_engine = sqlalchemy.create_engine


def _test_create_engine(url, **kwargs):
    url_str = str(url) if url is not None else ""
    if "sqlite" in url_str:
        kwargs = dict(kwargs)
        kwargs.pop("connect_args", None)
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url_str or url_str.rstrip("/").endswith("sqlite://"):
            from sqlalchemy.pool import StaticPool

            kwargs["poolclass"] = StaticPool
    return _original_create_engine(url, **kwargs)


sqlalchemy.create_engine = _test_create_engine

os.environ.setdefault("ENVIRONMENT", "development")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import itertools
import sqlite3

import pytest
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from jose import JWTError, jwt
from sqlalchemy import BigInteger, Integer, event
from sqlalchemy.orm import Session, sessionmaker

from app.core import deps
from app.database import Base, engine, get_db
from app.main import app
from app.models.user import Usuario
from app.routes import user as user_routes
from app.utils.security import ALGORITHM, SECRET_KEY


@event.listens_for(engine, "connect")
def _sqlite_attach_core_schema(dbapi_connection, connection_record):
    if engine.dialect.name != "sqlite":
        return
    cur = dbapi_connection.cursor()
    try:
        cur.execute("ATTACH DATABASE ':memory:' AS core")
    except sqlite3.OperationalError as exc:
        if "already in use" not in str(exc).lower():
            raise
    finally:
        cur.close()


def _install_sqlite_integer_pk_autofill() -> None:
    """SQLite no autoincrementa BIGINT PK como PostgreSQL; asignamos IDs en tests."""
    if engine.dialect.name != "sqlite":
        return
    if getattr(Base.registry, "_sqlite_pk_autofill", False):
        return
    setattr(Base.registry, "_sqlite_pk_autofill", True)

    counters: dict[str, itertools.count] = {}

    def make_listener(attr_name: str, key: str):
        def _on_before_insert(mapper, connection, target):
            if getattr(target, attr_name, None) is not None:
                return
            if key not in counters:
                counters[key] = itertools.count(1)
            setattr(target, attr_name, next(counters[key]))

        return _on_before_insert

    for mapper in Base.registry.mappers:
        tbl = mapper.class_.__table__
        pk_cols = list(tbl.primary_key.columns)
        if len(pk_cols) != 1:
            continue
        pk = pk_cols[0]
        if not isinstance(pk.type, (Integer, BigInteger)):
            continue
        schema = tbl.schema or "main"
        attr = pk.key
        key = f"{schema}:{tbl.name}:{attr}"
        event.listen(
            mapper.class_,
            "before_insert",
            make_listener(attr, key),
            propagate=True,
        )


_install_sqlite_integer_pk_autofill()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Rutas que definen su propio `get_db` apuntando a SessionLocal: deben usar el mismo override que `app.database.get_db`.
_ROUTE_MODULES_WITH_LOCAL_GET_DB = (
    "app.routes.pedido",
    "app.routes.pago",
    "app.routes.carrito",
    "app.routes.carrito_detalle",
    "app.routes.favorito",
    "app.routes.token_recuperacion",
    "app.routes.pedido_detalle",
    "app.routes.sesion",
    "app.routes.auditoria",
)


def _iter_route_get_db_functions():
    for modname in _ROUTE_MODULES_WITH_LOCAL_GET_DB:
        try:
            mod = importlib.import_module(modname)
        except ImportError:
            continue
        fn = getattr(mod, "get_db", None)
        if callable(fn):
            yield fn


_bearer = HTTPBearer()


def get_current_user_testing(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        correo = payload.get("sub")
        if correo is None:
            raise exc
    except JWTError:
        raise exc
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario is None:
        raise exc
    return usuario


@pytest.fixture(autouse=True)
def _stub_email(monkeypatch):
    """Evita SMTP real en /auth/login (2FA)."""
    monkeypatch.setattr(user_routes, "enviar_codigo_email", lambda destino, codigo: None)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    for route_get_db in _iter_route_get_db_functions():
        app.dependency_overrides[route_get_db] = override_get_db
    app.dependency_overrides[deps.get_current_user] = get_current_user_testing

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.pop(get_db, None)
    for route_get_db in _iter_route_get_db_functions():
        app.dependency_overrides.pop(route_get_db, None)
    app.dependency_overrides.pop(deps.get_current_user, None)


@pytest.fixture
def auth_headers():
    def _headers(email: str, rol: str | None = None):
        payload: dict = {"sub": email}
        if rol is not None:
            payload["rol"] = rol
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"Authorization": f"Bearer {token}"}

    return _headers
