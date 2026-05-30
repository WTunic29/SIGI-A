"""Calificaciones: cliente crea y lista (cita sembrada en BD; sin depender de POST /citas/)."""

from datetime import datetime

from app.models.cita import Cita
from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.models.user import Usuario
from app.utils.security import hash_password


def _seed_cita(db_session):
    owner = Usuario(
        nombre="O",
        apellido="N",
        correo="calif_owner@test.com",
        password_hash=hash_password("x"),
        rol="negocio",
    )
    cli = Usuario(
        nombre="C",
        apellido="L",
        correo="calif_cli@test.com",
        password_hash=hash_password("x"),
        rol="cliente",
    )
    db_session.add(owner)
    db_session.add(cli)
    db_session.commit()
    neg = Negocio(
        id_usuario_propietario=owner.id_usuario,
        nombre_negocio="Centro Calificaciones",
        direccion="Calle 1",
    )
    db_session.add(neg)
    db_session.commit()
    emp = Empleado(
        id_negocio=neg.id_negocio,
        nombre="E",
        apellido="M",
    )
    db_session.add(emp)
    db_session.commit()
    cita = Cita(
        id_cliente=cli.id_usuario,
        id_negocio=neg.id_negocio,
        id_empleado=emp.id_empleado,
        fecha_hora_inicio=datetime(2030, 3, 1, 10, 0, 0),
        fecha_hora_fin=datetime(2030, 3, 1, 10, 45, 0),
        estado="completada",
    )
    db_session.add(cita)
    db_session.commit()
    return neg, cli, cita


class TestCalificacionRoutes:
    def test_cliente_crea_y_lista_calificacion(self, client, db_session, auth_headers):
        neg, cli, cita = _seed_cita(db_session)
        body = {
            "id_negocio": neg.id_negocio,
            "id_cita": cita.id_cita,
            "puntuacion": 5,
            "comentario": "Muy bien",
        }
        r = client.post(
            "/calificaciones/",
            json=body,
            headers=auth_headers("calif_cli@test.com"),
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["id_negocio"] == neg.id_negocio
        assert data["id_cliente"] == cli.id_usuario
        assert data["puntuacion"] == 5

        lst = client.get(
            "/calificaciones/",
            headers=auth_headers("calif_cli@test.com"),
        )
        assert lst.status_code == 200
        assert any(item["puntuacion"] == 5 for item in lst.json())
