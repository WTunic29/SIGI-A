"""Servicios y empleados (rutas con get_db central)."""

from app.models.negocio import Negocio
from app.models.user import Usuario
from app.utils.security import hash_password


class TestServicioEmpleadoRoutes:
    def _seed_negocio_user(self, db_session, email: str):
        u = Usuario(
            nombre="N",
            apellido="B",
            correo=email,
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(u)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=u.id_usuario,
            nombre_negocio="Barber",
            direccion="d",
        )
        db_session.add(neg)
        db_session.commit()
        return u, neg

    def test_crear_servicio_negocio(self, client, db_session, auth_headers):
        _, neg = self._seed_negocio_user(db_session, "svc_owner@test.com")
        body = {
            "id_negocio": neg.id_negocio,
            "nombre": "Corte",
            "descripcion": "Corte clásico",
            "duracion_minutos": 30,
            "precio": 25000.0,
        }
        r = client.post(
            "/servicios/",
            json=body,
            headers=auth_headers("svc_owner@test.com"),
        )
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["nombre"] == "Corte"
        assert data["id_negocio"] == neg.id_negocio

    def test_listar_servicios_negocio(self, client, db_session, auth_headers):
        _, neg = self._seed_negocio_user(db_session, "svc_list@test.com")
        client.post(
            "/servicios/",
            json={
                "id_negocio": neg.id_negocio,
                "nombre": "Afeitado",
                "duracion_minutos": 15,
                "precio": 10000.0,
            },
            headers=auth_headers("svc_list@test.com"),
        )
        r = client.get("/servicios/", headers=auth_headers("svc_list@test.com"))
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_crear_empleado_negocio(self, client, db_session, auth_headers):
        _, neg = self._seed_negocio_user(db_session, "emp_own@test.com")
        body = {
            "id_negocio": neg.id_negocio,
            "nombre": "Luis",
            "apellido": "Gómez",
            "telefono": "3001112233",
        }
        r = client.post(
            "/empleados/",
            json=body,
            headers=auth_headers("emp_own@test.com"),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["nombre"] == "Luis"
        assert data["id_negocio"] == neg.id_negocio

    def test_listar_empleados_cliente_ve_activos(self, client, db_session, auth_headers):
        owner, neg = self._seed_negocio_user(db_session, "emp_cli_own@test.com")
        client.post(
            "/empleados/",
            json={
                "id_negocio": neg.id_negocio,
                "nombre": "Ana",
                "apellido": "Ruiz",
            },
            headers=auth_headers("emp_cli_own@test.com"),
        )
        cli = Usuario(
            nombre="Vis",
            apellido="Cliente",
            correo="emp_vis@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        r = client.get("/empleados/", headers=auth_headers("emp_vis@test.com"))
        assert r.status_code == 200
        assert isinstance(r.json(), list)
