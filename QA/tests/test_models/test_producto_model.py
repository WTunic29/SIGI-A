from decimal import Decimal

import pytest

from app.models.negocio import Negocio
from app.models.producto import Producto
from app.models.user import Usuario
from app.utils.security import hash_password


@pytest.fixture
def db_with_producto(db_session):
    user = Usuario(
        nombre="A",
        apellido="B",
        correo="owner@test.com",
        password_hash=hash_password("secret"),
        rol="negocio",
    )
    db_session.add(user)
    db_session.commit()
    neg = Negocio(
        id_usuario_propietario=user.id_usuario,
        nombre_negocio="N",
        direccion="d",
    )
    db_session.add(neg)
    db_session.commit()
    p = Producto(
        id_negocio=neg.id_negocio,
        nombre="Cafe Especial",
        descripcion="Grano",
        precio=Decimal("10.00"),
        stock=5,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return db_session, p


def test_crear_producto_model(db_with_producto):
    _, producto = db_with_producto
    assert producto.id_producto is not None
    assert producto.nombre == "Cafe Especial"
    assert producto.stock == 5


def test_buscar_producto_model(db_with_producto):
    db, _ = db_with_producto
    producto = db.query(Producto).filter(Producto.nombre == "Cafe Especial").first()
    assert producto is not None
    assert producto.nombre == "Cafe Especial"
