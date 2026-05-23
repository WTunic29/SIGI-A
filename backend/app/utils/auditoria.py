from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.user import Usuario


def registrar_auditoria(
    db: Session,
    accion: str,
    modulo: str,
    detalle: str,
    request: Optional[Request] = None,
    usuario: Optional[Usuario] = None,
    tabla_afectada: Optional[str] = None,
    id_registro: Optional[int] = None,
    nivel: str = "INFO",
    resultado: str = "OK"
):
    try:
        ip = None
        user_agent = None
        metodo_http = None
        ruta = None

        if request:
            ip = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            metodo_http = request.method
            ruta = str(request.url.path)

        nuevo_log = Auditoria(
            id_usuario=usuario.id_usuario if usuario else None,
            correo_usuario=usuario.correo if usuario else None,
            rol_usuario=usuario.rol if usuario else None,
            accion=accion,
            modulo=modulo,
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            metodo_http=metodo_http,
            ruta=ruta,
            detalle=detalle,
            ip=ip,
            user_agent=user_agent,
            nivel=nivel,
            resultado=resultado,
            fecha=datetime.utcnow()
        )

        db.add(nuevo_log)
        db.commit()

    except Exception:
        db.rollback()