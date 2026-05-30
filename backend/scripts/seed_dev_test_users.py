"""Usuarios de prueba para desarrollo local (sin depender de SMTP)."""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.codigo_2fa import Codigo2FA
from app.models.user import Usuario
from app.utils.security import hash_password

CLIENTE = {
    "nombre": "Ana",
    "apellido": "Prueba",
    "correo": "cliente@test.com",
    "telefono": "3001112233",
    "password": "password123",
    "rol": "cliente",
}

NEGOCIO = {
    "nombre": "Carlos",
    "apellido": "Barbero",
    "correo": "negocio@test.com",
    "telefono": "3004445566",
    "password": "password123",
    "rol": "negocio",
}

CODIGO_2FA = "123456"


def upsert_user(db, data):
    user = db.query(Usuario).filter(Usuario.correo == data["correo"]).first()
    if not user:
        user = Usuario(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            telefono=data["telefono"],
            password_hash=hash_password(data["password"]),
            rol=data["rol"],
            estado="activo",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Creado: {data['correo']} ({data['rol']})")
    else:
        user.estado = "activo"
        user.password_hash = hash_password(data["password"])
        db.commit()
        print(f"Actualizado: {data['correo']} ({data['rol']})")
    return user


def fijar_codigo_2fa(db, user):
    db.query(Codigo2FA).filter(
        Codigo2FA.id_usuario == user.id_usuario,
        Codigo2FA.usado == False,
    ).update({"usado": True})
    db.add(
        Codigo2FA(
            id_usuario=user.id_usuario,
            codigo=hash_password(CODIGO_2FA),
            fecha_expiracion=datetime.utcnow() + timedelta(hours=24),
            usado=False,
            intentos=0,
        )
    )
    db.commit()


def main():
    db = SessionLocal()
    try:
        upsert_user(db, CLIENTE)
        upsert_user(db, NEGOCIO)
        for correo in (CLIENTE["correo"], NEGOCIO["correo"]):
            user = db.query(Usuario).filter(Usuario.correo == correo).first()
            fijar_codigo_2fa(db, user)
        print()
        print("Credenciales de prueba:")
        print(f"  Cliente: {CLIENTE['correo']} / {CLIENTE['password']}")
        print(f"  Negocio: {NEGOCIO['correo']} / {NEGOCIO['password']}")
        print(f"  Código 2FA (Verify): {CODIGO_2FA}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
