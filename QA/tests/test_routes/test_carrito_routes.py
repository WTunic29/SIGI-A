"""Carrito: usa get_db local en la ruta; override en conftest lo alinea al SQLite de tests."""

from app.models.user import Usuario
from app.utils.security import hash_password


class TestCarritoRoutes:
    def test_crear_carrito_cliente(self, client, db_session, auth_headers):
        cli = Usuario(
            nombre="C",
            apellido="R",
            correo="cart_cli@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        r = client.post(
            "/carritos/",
            json={"id_usuario": cli.id_usuario, "estado": "activo"},
            headers=auth_headers("cart_cli@test.com"),
        )
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert "id_carrito" in data
        assert data["id_usuario"] == cli.id_usuario
