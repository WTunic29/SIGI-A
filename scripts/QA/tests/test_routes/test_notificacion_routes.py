"""Notificaciones: creación solo admin; listado para roles autenticados."""

from app.models.user import Usuario
from app.utils.security import hash_password


class TestNotificacionRoutes:
    def test_admin_crea_notificacion_y_se_lista(self, client, db_session, auth_headers):
        admin = Usuario(
            nombre="A",
            apellido="D",
            correo="admin_notif@test.com",
            password_hash=hash_password("x"),
            rol="admin",
        )
        cli = Usuario(
            nombre="U",
            apellido="S",
            correo="usr_notif@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(admin)
        db_session.add(cli)
        db_session.commit()

        body = {
            "id_usuario": cli.id_usuario,
            "titulo": "Aviso",
            "mensaje": "Mensaje de prueba QA",
            "tipo": "sistema",
        }
        r = client.post(
            "/notificaciones/",
            json=body,
            headers=auth_headers("admin_notif@test.com"),
        )
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert "id_notificacion" in data
        assert data["titulo"] == "Aviso"

        lst = client.get(
            "/notificaciones/",
            headers=auth_headers("usr_notif@test.com"),
        )
        assert lst.status_code == 200
        items = lst.json()
        assert any(n["titulo"] == "Aviso" for n in items)

    def test_cliente_no_puede_crear_notificacion(self, client, db_session, auth_headers):
        cli = Usuario(
            nombre="C",
            apellido="L",
            correo="cli_notif@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        r = client.post(
            "/notificaciones/",
            json={
                "id_usuario": cli.id_usuario,
                "titulo": "X",
                "mensaje": "Y",
                "tipo": "sistema",
            },
            headers=auth_headers("cli_notif@test.com"),
        )
        assert r.status_code == 403
