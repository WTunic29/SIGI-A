"""Inventario: movimiento de entrada y listado por producto."""

from decimal import Decimal

from app.models.negocio import Negocio
from app.models.producto import Producto
from app.models.user import Usuario
from app.utils.security import hash_password


class TestInventarioRoutes:
    def test_negocio_registra_entrada_y_lista_movimientos(
        self, client, db_session, auth_headers
    ):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="inv_owner@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Stock QA",
            direccion="Bodega 1",
        )
        db_session.add(neg)
        db_session.commit()
        prod = Producto(
            id_negocio=neg.id_negocio,
            nombre="Aceite",
            precio=Decimal("10000.00"),
            stock=10,
        )
        db_session.add(prod)
        db_session.commit()

        r = client.post(
            "/inventario-movimientos/",
            json={
                "id_producto": prod.id_producto,
                "tipo_movimiento": "entrada",
                "cantidad": 5,
                "motivo": "Reposición QA",
            },
            headers=auth_headers("inv_owner@test.com"),
        )
        assert r.status_code == 200, r.text
        mov = r.json()
        assert mov["tipo_movimiento"] == "entrada"
        assert mov["cantidad"] == 5
        assert mov["id_producto"] == prod.id_producto

        lst = client.get(
            f"/inventario-movimientos/{prod.id_producto}",
            headers=auth_headers("inv_owner@test.com"),
        )
        assert lst.status_code == 200
        items = lst.json()
        assert len(items) >= 1
        assert items[0]["tipo_movimiento"] == "entrada"
