import pytest
from decimal import Decimal
from app.models.user import Usuario
from app.models.negocio import Negocio
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate
from app.utils.security import hash_password

class TestProductoRoutes:
    """Test suite para Producto routes basados en código real"""
    
    def test_create_producto_success(self, client, db_session, auth_headers):
        """Test creación exitosa de producto"""
        # Crear usuario y negocio
        user = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        db_session.add(user)
        db_session.commit()
        
        negocio = Negocio(
            id_usuario_propietario=user.id_usuario,
            nombre_negocio="Barbería Central",
            direccion="Calle Principal 123"
        )
        db_session.add(negocio)
        db_session.commit()
        
        producto_data = {
            "id_negocio": negocio.id_negocio,
            "nombre": "Café Premium",
            "descripcion": "Café colombiano de alta calidad",
            "precio": "15000.00",
            "stock": 10,
            "imagen_url": "https://imagen.com/cafe.jpg"
        }
        
        response = client.post(
            "/productos/",
            json=producto_data,
            headers=auth_headers("carlos@test.com")
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Café Premium"
        assert data["precio"] == "15000.00"
        assert data["id_negocio"] == negocio.id_negocio
    
    def test_create_producto_unauthorized(self, client, db_session, auth_headers):
        """Test creación de producto por no propietario"""
        # Crear dos usuarios y negocios
        owner = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        other_user = Usuario(
            nombre="Otro",
            apellido="Usuario",
            correo="otro@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        
        db_session.add(owner)
        db_session.add(other_user)
        db_session.commit()
        
        negocio = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Barbería de Carlos",
            direccion="Dirección 123"
        )
        db_session.add(negocio)
        db_session.commit()
        
        producto_data = {
            "id_negocio": negocio.id_negocio,
            "nombre": "Producto No Autorizado",
            "precio": "1000.00",
            "stock": 5
        }
        
        response = client.post(
            "/productos/",
            json=producto_data,
            headers=auth_headers("otro@test.com")
        )
        
        assert response.status_code == 403
    
    def test_create_producto_unauthenticated(self, client):
        """Test creación de producto sin autenticación"""
        producto_data = {
            "id_negocio": 1,
            "nombre": "Producto Sin Auth",
            "precio": "1000.00",
            "stock": 5
        }
        
        response = client.post("/productos/", json=producto_data)
        
        assert response.status_code == 401
    
    def test_get_productos_by_negocio(self, client, db_session):
        """Test obtener productos por negocio"""
        # Crear usuario y negocio
        user = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        db_session.add(user)
        db_session.commit()
        
        negocio = Negocio(
            id_usuario_propietario=user.id_usuario,
            nombre_negocio="Barbería Central",
            direccion="Calle Principal 123"
        )
        db_session.add(negocio)
        db_session.commit()
        
        # Crear productos
        productos = []
        for i in range(3):
            producto = Producto(
                id_negocio=negocio.id_negocio,
                nombre=f"Producto {i+1}",
                descripcion=f"Descripción {i+1}",
                precio=Decimal(f"{(i+1)*1000}.00"),
                stock=10
            )
            db_session.add(producto)
            productos.append(producto)
        
        db_session.commit()
        
        response = client.get(f"/productos/negocio/{negocio.id_negocio}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_get_productos_negocio_not_found(self, client):
        """Test obtener productos de negocio inexistente"""
        response = client.get("/productos/negocio/99999")
        
        assert response.status_code == 404
        assert "Negocio no encontrado" in response.json()["detail"]
