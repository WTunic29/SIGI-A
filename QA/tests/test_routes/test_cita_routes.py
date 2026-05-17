"""
Contrato de citas.

xfail: el backend actual usa en `crear_cita` atributos `Cita.fecha` / `hora_inicio` / `hora_fin`
que no existen en `app.models.Cita` (el modelo define `fecha_hora_inicio` / `fecha_hora_fin`).
Cuando se corrija el backend, este test debería pasar (XPASS) y habrá que quitar el xfail.
"""

import pytest

from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.utils.security import hash_password


class TestCitaRoutes:
    def _seed_cita_context(self, db_session):
        owner = Usuario(
            nombre="O",
            apellido="N",
            correo="cita_owner@test.com",
            password_hash=hash_password("x"),
            rol="negocio",
        )
        db_session.add(owner)
        db_session.commit()
        neg = Negocio(
            id_usuario_propietario=owner.id_usuario,
            nombre_negocio="Centro",
            direccion="d",
        )
        db_session.add(neg)
        db_session.commit()
        emp = Empleado(
            id_negocio=neg.id_negocio,
            nombre="E",
            apellido="M",
        )
        db_session.add(emp)
        cli = Usuario(
            nombre="C",
            apellido="I",
            correo="cita_cli@test.com",
            password_hash=hash_password("x"),
            rol="cliente",
        )
        db_session.add(cli)
        db_session.commit()
        return neg, emp, cli

    @pytest.mark.xfail(
        reason=(
            "Bug backend: app.routes.cita usa Cita.fecha/hora_* pero app.models.Cita "
            "solo tiene fecha_hora_inicio/fin (AttributeError)."
        ),
        strict=False,
    )
    def test_cita_creacion_y_actualizacion_estado(self, client, db_session, auth_headers):
        neg, emp, cli = self._seed_cita_context(db_session)
        payload = {
            "id_negocio": neg.id_negocio,
            "id_empleado": emp.id_empleado,
            "fecha": "2030-06-15",
            "hora_inicio": "10:00:00",
            "hora_fin": "10:45:00",
            "observaciones": "test QA",
        }
        r = client.post(
            "/citas/",
            json=payload,
            headers=auth_headers("cita_cli@test.com"),
        )
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert "id_cita" in data
        assert data["id_cliente"] == cli.id_usuario
        assert data["id_negocio"] == neg.id_negocio
        assert data["id_empleado"] == emp.id_empleado

        id_cita = data["id_cita"]
        r2 = client.put(
            f"/citas/{id_cita}",
            json={"estado": "confirmada"},
            headers=auth_headers("cita_owner@test.com"),
        )
        assert r2.status_code == 200, r2.text
        assert r2.json().get("estado") == "confirmada"
