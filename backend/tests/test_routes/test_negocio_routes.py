import pytest
from app.models.user import Usuario
from app.models.negocio import Negocio
from app.schemas.negocio import NegocioCreate, NegocioUpdate
from app.utils.security import hash_password

class TestNegocioRoutes:
    """Test suite para Negocio routes basados en código real"""
    
    def test_create_negocio_success(self, client, db_session, auth_headers):
        """Test creación exitosa de negocio"""
        # Crear usuario negocio
        user = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        db_session.add(user)
        db_session.commit()
        
        negocio_data = {
            "nombre": "Barbería Central",
            "descripcion": "Mejor barbería de la ciudad",
            "direccion": "Calle Principal 123",
            "telefono": "555-1234",
            "correo": "barberia@test.com"
        }
        
        response = client.post(
            "/negocios/",
            json=negocio_data,
            headers=auth_headers("carlos@test.com")
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre_negocio"] == "Barbería Central"
        assert data["descripcion"] == "Mejor barbería de la ciudad"
    
    def test_create_negocio_unauthorized_role(self, client, db_session, auth_headers):
        """Test creación de negocio con rol no autorizado"""
        # Crear usuario cliente
        user = Usuario(
            nombre="Juan",
            apellido="Cliente",
            correo="juan@test.com",
            password_hash=hash_password("password123"),
            rol="cliente"
        )
        db_session.add(user)
        db_session.commit()
        
        negocio_data = {
            "nombre": "Barbería No Autorizada",
            "direccion": "Calle Test 123",
            "telefono": "555-1234"
        }
        
        response = client.post(
            "/negocios/",
            json=negocio_data,
            headers=auth_headers("juan@test.com")
        )
        
        assert response.status_code == 403
    
    def test_create_negocio_unauthenticated(self, client):
        """Test creación de negocio sin autenticación"""
        negocio_data = {
            "nombre": "Barbería Sin Auth",
            "direccion": "Calle Test 123"
        }
        
        response = client.post("/negocios/", json=negocio_data)
        
        assert response.status_code == 401
    
    def test_get_negocios_public(self, client, db_session):
        """Test obtener lista pública de negocios"""
        # Crear usuario y negocios
        user = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        db_session.add(user)
        db_session.commit()
        
        negocio1 = Negocio(
            id_usuario_propietario=user.id_usuario,
            nombre_negocio="Barbería 1",
            descripcion="Primera barbería",
            direccion="Dirección 1",
            telefono="555-1234"
        )
        negocio2 = Negocio(
            id_usuario_propietario=user.id_usuario,
            nombre_negocio="Spa 1",
            descripcion="Primer spa",
            direccion="Dirección 2",
            telefono="555-5678"
        )
        
        db_session.add(negocio1)
        db_session.add(negocio2)
        db_session.commit()
        
        response = client.get("/negocios/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_get_negocio_by_id_success(self, client, db_session):
        """Test obtener negocio por ID"""
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
            nombre_negocio="Barbería Test",
            descripcion="Descripción test",
            direccion="Test 123",
            telefono="555-1234"
        )
        db_session.add(negocio)
        db_session.commit()
        
        response = client.get(f"/negocios/{negocio.id_negocio}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_negocio"] == "Barbería Test"
        assert data["descripcion"] == "Descripción test"
    
    def test_get_negocio_not_found(self, client):
        """Test obtener negocio inexistente"""
        response = client.get("/negocios/99999")
        
        assert response.status_code == 404
        assert "Negocio no encontrado" in response.json()["detail"]
    
    def test_update_negocio_success(self, client, db_session, auth_headers):
        """Test actualización exitosa de negocio"""
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
            nombre_negocio="Barbería Original",
            descripcion="Descripción original",
            direccion="Dirección Original",
            telefono="555-1234"
        )
        db_session.add(negocio)
        db_session.commit()
        
        update_data = {
            "nombre": "Barbería Actualizada",
            "descripcion": "Descripción actualizada",
            "telefono": "555-9999"
        }
        
        response = client.put(
            f"/negocios/{negocio.id_negocio}",
            json=update_data,
            headers=auth_headers("carlos@test.com")
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_negocio"] == "Barbería Actualizada"
        assert data["descripcion"] == "Descripción actualizada"
        assert data["telefono"] == "555-9999"
    
    def test_update_negocio_unauthorized(self, client, db_session, auth_headers):
        """Test actualización de negocio por no propietario"""
        # Crear dos usuarios
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
            descripcion="Descripción",
            direccion="Dirección 123",
            telefono="555-1234"
        )
        db_session.add(negocio)
        db_session.commit()
        
        update_data = {
            "nombre": "Barbería Hackeada"
        }
        
        response = client.put(
            f"/negocios/{negocio.id_negocio}",
            json=update_data,
            headers=auth_headers("otro@test.com")
        )
        
        assert response.status_code == 403
    
    def test_delete_negocio_success(self, client, db_session, auth_headers):
        """Test eliminación exitosa de negocio"""
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
            nombre_negocio="Barbería a Eliminar",
            descripcion="Descripción",
            direccion="Dirección 123",
            telefono="555-1234"
        )
        db_session.add(negocio)
        db_session.commit()
        
        response = client.delete(
            f"/negocios/{negocio.id_negocio}",
            headers=auth_headers("carlos@test.com")
        )
        
        assert response.status_code == 200
        assert "Negocio eliminado" in response.json()["message"]
    
    def test_delete_negocio_unauthorized(self, client, db_session, auth_headers):
        """Test eliminación de negocio por no propietario"""
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
            descripcion="Descripción",
            direccion="Dirección 123",
            telefono="555-1234"
        )
        db_session.add(negocio)
        db_session.commit()
        
        response = client.delete(
            f"/negocios/{negocio.id_negocio}",
            headers=auth_headers("otro@test.com")
        )
        
        assert response.status_code == 403
    
    def test_create_negocio_validation_error(self, client, db_session, auth_headers):
        """Test creación de negocio con datos inválidos"""
        user = Usuario(
            nombre="Carlos",
            apellido="Dueño",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="negocio"
        )
        db_session.add(user)
        db_session.commit()
        
        # Datos inválidos (email mal formateado)
        negocio_data = {
            "nombre": "Barbería Test",
            "correo": "email_invalido"
        }
        
        response = client.post(
            "/negocios/",
            json=negocio_data,
            headers=auth_headers("carlos@test.com")
        )
        
        assert response.status_code == 422
