from decimal import Decimal
from app.models.producto import Producto
from tests.conftest import TestingSessionLocal

def test_crear_producto_model():

    db = TestingSessionLocal()

    producto = Producto(

        id_negocio=1,
        nombre="",
        descripcion="",
        precio=Decimal(""),
        stock=5,
        imagen_url=""
    )

    db.add(producto)
    db.commit()
    db.refresh(producto)

    assert producto.id_producto is not None
    assert producto.nombre == "Cafe Especial"
    assert producto.stock == 5

    db.close()

def test_buscar_producto_model():

    db = TestingSessionLocal()

    producto = db.query(Producto).filter(
        Producto.nombre == "Cafe Especial"
    ).first()

    assert producto is not None
    assert producto.nombre == "Cafe Especial"

    db.close()
