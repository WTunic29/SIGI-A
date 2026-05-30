"""Favoritos: cliente crea y lista (get_db local; override en conftest)."""

from app.models.negocio import Negocio
from app.models.user import Usuario
from app.utils.security import hash_password


class TestFavoritoRoutes:
    def test_cliente_crea_y_lista_favorito(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="fav_owner@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        cli = Usuario(
            nombre="C",
            apellido="L",
            correo="fav_cli@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(owner)
        db_session.add(cli)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Favorito Spa",
            direccion="Av 2",
        )
        db_session.add(neg)
        db_session.commit()

        r = client.post(
            "/favoritos/",
            json={
                "id_usuario": cli.id_usuario,
                "id_negocio": neg.id_negocio,
            },
            headers=auth_headers("fav_cli@test.com"),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["id_negocio"] == neg.id_negocio
        assert data["id_usuario"] == cli.id_usuario
        assert "id_favorito" in data

        lst = client.get(
            "/favoritos/",
            headers=auth_headers("fav_cli@test.com"),
        )
        assert lst.status_code == 200
        assert any(f["id_negocio"] == neg.id_negocio for f in lst.json())
