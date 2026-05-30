import pytest

from decimal import Decimal
from pydantic import ValidationError

from app.schemas.producto import ProductoCreate

def test_producto_schema_valido():

    producto = ProductoCreate(
        id_negocio=1,
        nombre="Cafe Premium",
        descripcion="Cafe colombiano",
        precio=Decimal("15000.00"),
        stock=10,
        imagen_url="https://imagen.com/cafe.jpg"
    )

    assert producto.nombre == "Cafe Premium"
    assert producto.stock == 10

def test_producto_schema_invalido():

    with pytest.raises(ValidationError):

        ProductoCreate(
            id_negocio="texto",
            nombre=123,
            precio="abc",
            stock="muchos"
        )
