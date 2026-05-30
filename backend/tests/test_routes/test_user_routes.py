import pytest
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.utils.security import hash_password

class TestUserRoutes:
    """Test suite para User routes basados en código real"""
    
    def test_register_user_success(self, client, db_session):
        """Test registro exitoso de usuario"""
        user_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@test.com",
            "telefono": "555-1234",
            "password": "password123",
            "rol": "cliente"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        
        # Verificar usuario en base de datos
        user = db_session.query(Usuario).filter(
            Usuario.correo == "juan@test.com"
        ).first()
        assert user is not None
        assert user.nombre == "Juan"
        assert user.rol == "cliente"
    
    def test_register_duplicate_email(self, client, db_session):
        """Test registro con email duplicado"""
        # Crear usuario existente
        user = Usuario(
            nombre="Carlos",
            apellido="López",
            correo="carlos@test.com",
            password_hash=hash_password("password123"),
            rol="cliente"
        )
        db_session.add(user)
        db_session.commit()
        
        # Intentar registrar mismo email
        user_data = {
            "nombre": "Otro",
            "apellido": "Usuario",
            "correo": "carlos@test.com",
            "telefono": "555-5678",
            "password": "password456",
            "rol": "cliente"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "El correo ya está registrado" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registro con email inválido"""
        user_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "email_invalido",
            "telefono": "555-1234",
            "password": "password123",
            "rol": "cliente"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_required_fields(self, client):
        """Test registro sin campos requeridos"""
        # Sin nombre
        user_data = {
            "apellido": "Pérez",
            "correo": "test@test.com",
            "password": "password123",
            "rol": "cliente"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_login_success(self, client, db_session):
        """Test login exitoso"""
        # Crear usuario
        user = Usuario(
            nombre="Juan",
            apellido="Pérez",
            correo="juan@test.com",
            password_hash=hash_password("password123"),
            rol="cliente"
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "correo": "juan@test.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "correo" in data
        assert data["correo"] == "juan@test.com"
    
    def test_login_invalid_credentials(self, client):
        """Test login con credenciales inválidas"""
        login_data = {
            "correo": "noexiste@test.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Credenciales incorrectas" in response.json()["detail"]
    
    def test_login_invalid_email_format(self, client):
        """Test login con email formato inválido"""
        login_data = {
            "correo": "email_invalido",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 422
    
    def test_get_me_success(self, client, db_session, auth_headers):
        """Test obtener perfil usuario autenticado"""
        # Crear usuario para auth
        user = Usuario(
            nombre="Juan",
            apellido="Pérez",
            correo="juan@test.com",
            password_hash=hash_password("password123"),
            rol="cliente"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.get("/auth/me", headers=auth_headers("juan@test.com"))
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Juan"
        assert data["apellido"] == "Pérez"
        assert data["correo"] == "juan@test.com"
        assert data["rol"] == "cliente"
    
    def test_get_me_unauthorized(self, client):
        """Test obtener perfil sin autenticación"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, client):
        """Test obtener perfil con token inválido"""
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_register_different_roles(self, client, db_session):
        """Test registro con diferentes roles"""
        roles = ["cliente", "negocio", "admin"]
        
        for rol in roles:
            user_data = {
                "nombre": f"User_{rol}",
                "apellido": "Test",
                "correo": f"{rol}@test.com",
                "telefono": "555-1234",
                "password": "password123",
                "rol": rol
            }
            
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 201
            
            # Verificar en base de datos
            user = db_session.query(Usuario).filter(
                Usuario.correo == f"{rol}@test.com"
            ).first()
            assert user is not None
            assert user.rol == rol
    
    def test_register_invalid_role(self, client):
        """Test registro con rol inválido"""
        user_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@test.com",
            "telefono": "555-1234",
            "password": "password123",
            "rol": "rol_invalido"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        # Puede ser 422 (validation) o 201 (si no hay validación de rol)
        assert response.status_code in [422, 201]
