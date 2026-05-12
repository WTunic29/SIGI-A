"""
Tests standalone para schemas sin dependencias de base de datos
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

# Import directo de schemas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.schemas.user import UsuarioCreate, UsuarioLogin, Verificar2FA
from app.schemas.negocio import NegocioCreate, NegocioUpdate
from app.schemas.producto import ProductoCreate

class TestUserSchemas:
    """Test suite para User schemas"""
    
    def test_usuario_create_valid(self):
        """Test UsuarioCreate con datos válidos"""
        user_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@test.com",
            "telefono": "555-1234",
            "password": "password123",
            "rol": "cliente"
        }
        user = UsuarioCreate(**user_data)
        assert user.nombre == "Juan"
        assert user.correo == "juan@test.com"
        assert user.rol == "cliente"
    
    def test_usuario_create_invalid_email(self):
        """Test UsuarioCreate con email inválido"""
        user_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "email_invalido",
            "telefono": "555-1234",
            "password": "password123",
            "rol": "cliente"
        }
        with pytest.raises(ValidationError):
            UsuarioCreate(**user_data)

class TestNegocioSchemas:
    """Test suite para Negocio schemas"""
    
    def test_negocio_create_valid(self):
        """Test NegocioCreate con datos válidos"""
        negocio_data = {
            "nombre": "Barbería Central",
            "descripcion": "Mejor barbería de la ciudad",
            "direccion": "Calle Principal 123",
            "telefono": "555-1234",
            "correo": "barberia@test.com"
        }
        negocio = NegocioCreate(**negocio_data)
        assert negocio.nombre == "Barbería Central"
        assert negocio.descripcion == "Mejor barbería de la ciudad"

class TestProductoSchemas:
    """Test suite para Producto schemas"""
    
    def test_producto_create_valid(self):
        """Test ProductoCreate con datos válidos"""
        producto_data = {
            "id_negocio": 1,
            "nombre": "Café Premium",
            "descripcion": "Café colombiano de alta calidad",
            "precio": Decimal("15000.00"),
            "stock": 10,
            "imagen_url": "https://imagen.com/cafe.jpg"
        }
        producto = ProductoCreate(**producto_data)
        assert producto.nombre == "Café Premium"
        assert producto.precio == Decimal("15000.00")
        assert producto.stock == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
