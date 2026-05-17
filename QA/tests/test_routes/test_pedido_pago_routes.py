"""Pedidos y pagos: contrato esperado (respuesta plana, roles)."""

from decimal import Decimal

from app.models.negocio import Negocio
from app.models.user import Usuario
from app.utils.security import hash_password


class TestPedidoRoutes:
    def test_crear_pedido_cliente_ok(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="Dueño",
            apellido="Negocio",
            correo="owner_ped@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="N1",
            direccion="calle",
        )
        db_session.add(neg)
        cliente = Usuario(
            nombre="Cli",
            apellido="Pedido",
            correo="cli_ped@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cliente)
        db_session.commit()

        body = {
            "id_usuario": cliente.id_usuario,
            "id_negocio": neg.id_negocio,
            "total": "150.50",
            "estado": "pendiente",
        }
        r = client.post(
            "/pedidos/",
            json=body,
            headers=auth_headers("cli_ped@test.com"),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id_pedido" in data
        assert data["id_usuario"] == cliente.id_usuario
        assert data["id_negocio"] == neg.id_negocio
        assert Decimal(str(data["total"])) == Decimal("150.50")

    def test_crear_pedido_negocio_forbidden(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="onlyneg@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Nx",
            direccion="d",
        )
        db_session.add(neg)
        db_session.commit()

        body = {
            "id_usuario": owner.id_usuario,
            "id_negocio": neg.id_negocio,
            "total": "10.00",
            "estado": "pendiente",
        }
        r = client.post(
            "/pedidos/",
            json=body,
            headers=auth_headers("onlyneg@test.com"),
        )
        assert r.status_code == 403

    def test_listar_pedidos_cliente(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="own2@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="N2",
            direccion="d",
        )
        db_session.add(neg)
        cli = Usuario(
            nombre="C",
            apellido="L",
            correo="cli2@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        client.post(
            "/pedidos/",
            json={
                "id_usuario": cli.id_usuario,
                "id_negocio": neg.id_negocio,
                "total": "20.00",
                "estado": "pendiente",
            },
            headers=auth_headers("cli2@test.com"),
        )
        r = client.get("/pedidos/", headers=auth_headers("cli2@test.com"))
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1


class TestPagoRoutes:
    def test_crear_pago_cliente_ok(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="ownp@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Np",
            direccion="d",
        )
        db_session.add(neg)
        cli = Usuario(
            nombre="C",
            apellido="P",
            correo="clip@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        pr = client.post(
            "/pedidos/",
            json={
                "id_usuario": cli.id_usuario,
                "id_negocio": neg.id_negocio,
                "total": "100.00",
                "estado": "pendiente",
            },
            headers=auth_headers("clip@test.com"),
        )
        assert pr.status_code == 200
        id_pedido = pr.json()["id_pedido"]

        r = client.post(
            "/pagos/",
            json={
                "id_pedido": id_pedido,
                "metodo_pago": "tarjeta",
                "referencia_externa": "REF-TEST-1",
                "estado_pago": "pendiente",
                "valor": "50.00",
            },
            headers=auth_headers("clip@test.com"),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id_pago" in data
        assert data["id_pedido"] == id_pedido

    def test_listar_pagos_cliente(self, client, db_session, auth_headers):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="ownlp@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Nlp",
            direccion="d",
        )
        db_session.add(neg)
        cli = Usuario(
            nombre="C",
            apellido="L",
            correo="clilp@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        pr = client.post(
            "/pedidos/",
            json={
                "id_usuario": cli.id_usuario,
                "id_negocio": neg.id_negocio,
                "total": "80.00",
                "estado": "pendiente",
            },
            headers=auth_headers("clilp@test.com"),
        )
        id_pedido = pr.json()["id_pedido"]
        client.post(
            "/pagos/",
            json={
                "id_pedido": id_pedido,
                "metodo_pago": "efectivo",
                "estado_pago": "aprobado",
                "valor": "80.00",
            },
            headers=auth_headers("clilp@test.com"),
        )
        r = client.get("/pagos/", headers=auth_headers("clilp@test.com"))
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 1
