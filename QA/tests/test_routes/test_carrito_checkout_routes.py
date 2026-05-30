"""Tests de carrito activo y checkout (SQLite en memoria)."""

from decimal import Decimal

from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.negocio import Negocio
from app.models.producto import Producto
from app.models.user import Usuario
from app.utils.security import hash_password


class TestCarritoCheckout:
    def _seed_cliente_negocio_producto(self, db_session):
        prop = Usuario(
            nombre="N",
            apellido="E",
            correo="prop_checkout@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        cli = Usuario(
            nombre="C",
            apellido="L",
            correo="cli_checkout@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add_all([prop, cli])
        db_session.flush()

        neg = Negocio(
            id_usuario_propietario=prop.id_usuario,
            nombre_negocio="Salon Test",
            direccion="calle test",
        )
        db_session.add(neg)
        db_session.flush()

        prod = Producto(
            id_negocio=neg.id_negocio,
            nombre="Shampoo",
            precio=Decimal("25000"),
            stock=10,
            estado="activo",
        )
        db_session.add(prod)
        db_session.commit()
        return cli, neg, prod

    def test_carrito_activo_me(self, client, db_session, auth_headers):
        cli, neg, prod = self._seed_cliente_negocio_producto(db_session)
        headers = auth_headers("cli_checkout@test.com")

        r = client.get("/carritos/activo/me", headers=headers)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "carrito" in data
        assert data["carrito"]["estado"] == "activo"
        assert data["cantidad_items"] == 0

        carrito_id = data["carrito"]["id_carrito"]
        r2 = client.post(
            "/carrito-detalle/",
            json={
                "id_carrito": carrito_id,
                "tipo_item": "producto",
                "id_negocio": neg.id_negocio,
                "id_producto": prod.id_producto,
                "cantidad": 2,
                "precio_unitario": "25000",
            },
            headers=headers,
        )
        assert r2.status_code == 200, r2.text

        r3 = client.get("/carritos/activo/me", headers=headers)
        assert r3.status_code == 200
        assert r3.json()["cantidad_items"] == 1
        assert r3.json()["total"] == 50000.0

    def test_checkout_producto_genera_factura(self, client, db_session, auth_headers):
        cli, neg, prod = self._seed_cliente_negocio_producto(db_session)
        headers = auth_headers("cli_checkout@test.com")

        carrito = client.get("/carritos/activo/me", headers=headers).json()
        carrito_id = carrito["carrito"]["id_carrito"]

        client.post(
            "/carrito-detalle/",
            json={
                "id_carrito": carrito_id,
                "tipo_item": "producto",
                "id_negocio": neg.id_negocio,
                "id_producto": prod.id_producto,
                "cantidad": 1,
                "precio_unitario": "25000",
            },
            headers=headers,
        )

        checkout = client.post(
            f"/carritos/{carrito_id}/checkout",
            json={"metodo_pago": "efectivo", "referencia_externa": "TEST-1"},
            headers=headers,
        )
        assert checkout.status_code == 200, checkout.text
        body = checkout.json()
        assert body["facturas"]
        assert body["pedidos"][0]["estado"] == "pagado"

        id_factura = body["facturas"][0]["id_factura"]
        factura = client.get(f"/facturas/{id_factura}", headers=headers)
        assert factura.status_code == 200
        assert factura.json()["numero_factura"].startswith("FAC-")
