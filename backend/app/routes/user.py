import os
import secrets
from datetime import datetime, timedelta
import base64
from io import BytesIO
import hashlib

import pyotp
import qrcode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.rate_limit import limiter
from app.utils.auditoria import registrar_auditoria

from app.models.codigo_2fa import Codigo2FA
from app.models.sesion import Sesion
from app.models.user import Usuario
from app.models.token_activacion import TokenActivacion
from app.models.token_recuperacion import TokenRecuperacion

from app.schemas.user import (
    UsuarioCreate,
    UsuarioLogin,
    Verificar2FA,
    CambiarRolUsuario,
    CambiarEstadoUsuario,
    ConfirmarMFA,
    VerificarMFA,
    ForgotPasswordRequest,
    ResetPasswordRequest
)


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:10000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")

from app.utils.email import (
    enviar_codigo_email,
    enviar_link_activacion_email,
    enviar_link_recuperacion_email
)

from app.utils.security import (
    SECRET_KEY,
    ALGORITHM,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter()


def contar_superadmins_activos(db: Session) -> int:
    return db.query(Usuario).filter(
        Usuario.rol == "superadmin",
        Usuario.estado == "activo"
    ).count()


def proteger_unico_superadmin_activo(
    db: Session,
    usuario: Usuario,
    nuevo_rol: str | None = None,
    nuevo_estado: str | None = None,
    accion: str = "modificar"
):
    rol_final = nuevo_rol if nuevo_rol is not None else usuario.rol
    estado_final = nuevo_estado if nuevo_estado is not None else usuario.estado

    deja_de_ser_superadmin_activo = (
        usuario.rol == "superadmin"
        and usuario.estado == "activo"
        and (
            rol_final != "superadmin"
            or estado_final != "activo"
            or accion == "eliminar"
        )
    )

    if deja_de_ser_superadmin_activo and contar_superadmins_activos(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar, cambiar rol ni cambiar estado de este usuario porque es el único superadministrador activo del sistema"
        )




def limpiar_usuarios_pendientes_expirados(db: Session, minutos: int = 5):
    """
    Elimina usuarios pendientes que no activaron la cuenta dentro del tiempo permitido.
    Esto permite que puedan registrarse nuevamente con el mismo correo.
    """
    from sqlalchemy import text

    db.execute(
        text("""
            DELETE FROM core.tokens_activacion
            WHERE id_usuario IN (
                SELECT id_usuario
                FROM core.usuarios
                WHERE estado = 'pendiente'
                AND fecha_creacion < NOW() - (:minutos * INTERVAL '1 minute')
            )
        """),
        {"minutos": minutos}
    )

    resultado = db.execute(
        text("""
            DELETE FROM core.usuarios
            WHERE estado = 'pendiente'
            AND fecha_creacion < NOW() - (:minutos * INTERVAL '1 minute')
        """),
        {"minutos": minutos}
    )

    db.commit()
    return resultado.rowcount or 0




# =========================
# USUARIO ACTUAL
# =========================

@router.get("/me")
def get_me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id_usuario,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "correo": current_user.correo,
        "rol": current_user.rol,
        "estado": current_user.estado
    }

# =========================
# MFA TOTP - SETUP QR
# =========================

@router.post("/mfa/setup")
def mfa_setup(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.mfa_totp_enabled:
        raise HTTPException(
            status_code=400,
            detail="El MFA con aplicación autenticadora ya está activo."
        )

    secret = pyotp.random_base32()

    current_user.mfa_totp_secret = secret
    db.commit()
    registrar_auditoria(
        db=db,
        usuario=current_user,
        accion="MFA_SETUP_QR_GENERADO",
        modulo="auth",
        tabla_afectada="core.usuarios",
        id_registro=current_user.id_usuario,
        detalle=f"Usuario {current_user.correo} generó QR para configurar MFA con aplicación autenticadora.",
        nivel="INFO",
        resultado="PENDIENTE"
    )

    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.correo,
        issuer_name="SIGI-A"
    )

    qr = qrcode.make(totp_uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "message": "Escanea este QR con Google Authenticator o Microsoft Authenticator.",
        "secret": secret,
        "qr_base64": f"data:image/png;base64,{qr_base64}"
    }

# =========================
# MFA TOTP - CONFIRMAR
# =========================

@router.post("/mfa/confirm")
def mfa_confirm(
    data: ConfirmarMFA,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.mfa_totp_secret:
        raise HTTPException(
            status_code=400,
            detail="Primero debes generar el QR de configuración MFA."
        )

    if current_user.mfa_totp_enabled:
        raise HTTPException(
            status_code=400,
            detail="El MFA con aplicación autenticadora ya está activo."
        )

    totp = pyotp.TOTP(current_user.mfa_totp_secret)

    if not totp.verify(data.codigo, valid_window=1):
        raise HTTPException(
            status_code=400,
            detail="Código MFA inválido o expirado."
        )

    current_user.mfa_totp_enabled = True
    db.commit()
    registrar_auditoria(
        db=db,
        usuario=current_user,
        accion="MFA_TOTP_ACTIVADO",
        modulo="auth",
        tabla_afectada="core.usuarios",
        id_registro=current_user.id_usuario,
        detalle=f"Usuario {current_user.correo} activó MFA con aplicación autenticadora correctamente.",
        nivel="INFO",
        resultado="OK"
    )

    return {
        "message": "MFA con aplicación autenticadora activado correctamente."
    }

# =========================
# MFA TOTP - VERIFICAR LOGIN
# =========================

@limiter.limit("5/minute")
@router.post("/mfa/verify")
def mfa_verify(
    data: VerificarMFA,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if usuario.estado != "activo":
        raise HTTPException(
            status_code=403,
            detail="La cuenta no está activa."
        )

    if not usuario.mfa_totp_enabled or not usuario.mfa_totp_secret:
        raise HTTPException(
            status_code=400,
            detail="El usuario no tiene MFA con aplicación autenticadora activo."
        )

    totp = pyotp.TOTP(usuario.mfa_totp_secret)

    if not totp.verify(data.codigo, valid_window=1):
        raise HTTPException(
            status_code=400,
            detail="Código MFA inválido o expirado."
        )

    access_token = create_access_token(
        data={
            "sub": usuario.correo,
            "id_usuario": usuario.id_usuario,
            "rol": usuario.rol
        }
    )

    refresh_token = create_refresh_token(
        data={
            "sub": usuario.correo,
            "id_usuario": usuario.id_usuario
        }
    )

    nueva_sesion = Sesion(
        id_usuario=usuario.id_usuario,
        token=access_token,
        fecha_inicio=datetime.utcnow(),
        fecha_expiracion=datetime.utcnow() + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        ),
        ip=request.client.host,
        user_agent=request.headers.get("user-agent"),
        activa=True
    )

    db.add(nueva_sesion)
    db.commit()
    registrar_auditoria(
        db=db,
        request=request,
        usuario=usuario,
        accion="LOGIN_MFA_TOTP_EXITOSO",
        modulo="auth",
        tabla_afectada="core.usuarios",
        id_registro=usuario.id_usuario,
        detalle=f"Usuario {usuario.correo} validó correctamente MFA con aplicación autenticadora.",
        nivel="INFO",
        resultado="OK"
    )

    return {
        "message": "MFA validado correctamente",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id_usuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "rol": usuario.rol,
            "estado": usuario.estado
        }
    }

# =========================
# REGISTRO
# =========================

@router.post("/register", status_code=201)
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):

    # Limpia usuarios pendientes que no activaron la cuenta en 5 minutos
    limpiar_usuarios_pendientes_expirados(db=db, minutos=5)

    try:
        existente = db.query(Usuario).filter(
            Usuario.correo == user.correo
        ).first()

        if existente:
            raise HTTPException(
                status_code=400,
                detail="El correo ya está registrado"
            )
        rol_solicitado = user.rol or "cliente"

        if rol_solicitado not in ["cliente", "negocio"]:
            raise HTTPException(
                status_code=400,
                detail="Rol no permitido para registro público"
            )

        nuevo_usuario = Usuario(
            nombre=user.nombre,
            apellido=user.apellido,
            correo=user.correo,
            telefono=user.telefono,
            genero=user.genero,
            password_hash=hash_password(user.password),
            rol=rol_solicitado,
            estado="pendiente"
        )


        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        token_activacion = secrets.token_urlsafe(48)

        nuevo_token = TokenActivacion(
            id_usuario=nuevo_usuario.id_usuario,
            token=token_activacion,
            fecha_expiracion=datetime.utcnow() + timedelta(hours=5),
            usado=False
        )

        db.add(nuevo_token)
        db.commit()

        link_activacion = (
            f"{BACKEND_URL}/auth/activar-cuenta"
            f"?token={token_activacion}"
        )

        enviar_link_activacion_email(
            nuevo_usuario.correo,
            link_activacion
        )

        registrar_auditoria(
            db=db,
            usuario=nuevo_usuario,
            accion="USUARIO_REGISTRADO",
            modulo="auth",
            tabla_afectada="core.usuarios",
            id_registro=nuevo_usuario.id_usuario,
            detalle=f"Usuario {nuevo_usuario.correo} se registró con estado pendiente. Se envió enlace de activación al correo.",
            nivel="INFO",
            resultado="OK"
        )

        return {
            "message": "Usuario creado correctamente. Revisa tu correo para activar la cuenta.",
            "usuario": {
                "id": nuevo_usuario.id_usuario,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
                "rol": nuevo_usuario.rol,
                "estado": nuevo_usuario.estado
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ACTIVAR CUENTA
# =========================

@router.get("/activar-cuenta")
def activar_cuenta(
    token: str,
    db: Session = Depends(get_db)
):
    frontend_url = f"{FRONTEND_URL}/activacion.html"

    token_db = db.query(TokenActivacion).filter(
        TokenActivacion.token == token,
        TokenActivacion.usado == False
    ).first()

    if not token_db:
        return RedirectResponse(
            url=f"{frontend_url}?estado=error&motivo=token_invalido"
        )

    if token_db.fecha_expiracion < datetime.utcnow():
        return RedirectResponse(
            url=f"{frontend_url}?estado=error&motivo=token_expirado"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == token_db.id_usuario
    ).first()

    if not usuario:
        return RedirectResponse(
            url=f"{frontend_url}?estado=error&motivo=usuario_no_encontrado"
        )

    if usuario.estado == "activo":
        token_db.usado = True
        db.commit()

        return RedirectResponse(
            url=f"{frontend_url}?estado=ok"
        )

    usuario.estado = "activo"
    token_db.usado = True
    db.commit()

    registrar_auditoria(
        db=db,
        usuario=usuario,
        accion="CUENTA_ACTIVADA",
        modulo="auth",
        tabla_afectada="core.usuarios",
        id_registro=usuario.id_usuario,
        detalle=f"Usuario {usuario.correo} activó su cuenta mediante enlace enviado al correo.",
        nivel="INFO",
        resultado="OK"
    )

    return RedirectResponse(
        url=f"{frontend_url}?estado=ok"
    )

# =========================
# OLVIDÉ CONTRASEÑA
# =========================

@limiter.limit("5/minute")
@router.post("/forgot-password")
def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == data.correo
    ).first()

    # Respuesta genérica para no revelar si el correo existe o no
    if not usuario:
        return {
            "message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
        }

    tokens_anteriores = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.id_usuario == usuario.id_usuario,
        TokenRecuperacion.usado == False
    ).all()

    for token_anterior in tokens_anteriores:
        token_anterior.usado = True

    token_raw = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()

    nuevo_token = TokenRecuperacion(
        id_usuario=usuario.id_usuario,
        token=token_hash,
        fecha_creacion=datetime.utcnow(),
        fecha_expiracion=datetime.utcnow() + timedelta(minutes=15),
        usado=False
    )

    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    link_recuperacion = (
        f"{FRONTEND_URL}/restablecer.html"
        f"?token={token_raw}"
    )

    enviar_link_recuperacion_email(
        usuario.correo,
        link_recuperacion
    )

    registrar_auditoria(
        db=db,
        request=request,
        usuario=usuario,
        accion="PASSWORD_RESET_LINK_ENVIADO",
        modulo="auth",
        tabla_afectada="core.tokens_recuperacion",
        id_registro=nuevo_token.id_token,
        detalle=f"Se envió enlace de recuperación de contraseña al correo {usuario.correo}",
        nivel="INFO",
        resultado="OK"
    )

    return {
        "message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
    }


# =========================
# RESTABLECER CONTRASEÑA
# =========================

@limiter.limit("5/minute")
@router.post("/reset-password")
def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()

    token_db = db.query(TokenRecuperacion).filter(
        TokenRecuperacion.token == token_hash,
        TokenRecuperacion.usado == False
    ).first()

    if not token_db:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o ya usado"
        )

    if token_db.fecha_expiracion < datetime.utcnow():
        token_db.usado = True
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación ha expirado"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == token_db.id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    usuario.password_hash = hash_password(data.nueva_password)
    usuario.estado = "activo"
    token_db.usado = True

    db.commit()

    registrar_auditoria(
        db=db,
        request=request,
        usuario=usuario,
        accion="PASSWORD_RESTABLECIDA",
        modulo="auth",
        tabla_afectada="core.usuarios",
        id_registro=usuario.id_usuario,
        detalle=f"Usuario {usuario.correo} restableció su contraseña correctamente",
        nivel="INFO",
        resultado="OK"
    )

    return {
        "message": "Contraseña restablecida correctamente. Ya puedes iniciar sesión."
    }

# =========================
# LOGIN
# =========================

@limiter.limit("5/minute")
@router.post("/login")
def login_user(
    request: Request,
    user: UsuarioLogin,
    db: Session = Depends(get_db)
):
    try:
        usuario = db.query(Usuario).filter(
            Usuario.correo == user.correo
        ).first()

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas"
            )

        if not verify_password(user.password, usuario.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas"
            )

        if usuario.estado != "activo":
            raise HTTPException(
                status_code=403,
                detail="La cuenta no está activa. Debes activar tu cuenta desde el correo enviado."
            )

        if usuario.mfa_totp_enabled:
            registrar_auditoria(
                db=db,
                request=request,
                usuario=usuario,
                accion="MFA_TOTP_SOLICITADO",
                modulo="auth",
                tabla_afectada="core.usuarios",
                id_registro=usuario.id_usuario,
                detalle=f"Usuario {usuario.correo} debe verificar MFA con aplicación autenticadora",
                nivel="INFO",
                resultado="PENDIENTE"
            )

            return {
                "message": "Ingresa el código de tu aplicación autenticadora.",
                "requiere_mfa": True,
                "metodo": "totp",
                "correo": usuario.correo
            }

        access_token = create_access_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario,
                "rol": usuario.rol
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario
            }
        )

        nueva_sesion = Sesion(
            id_usuario=usuario.id_usuario,
            token=access_token,
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            ),
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            activa=True
        )

        db.add(nueva_sesion)
        db.commit()

        registrar_auditoria(
            db=db,
            request=request,
            usuario=usuario,
            accion="LOGIN_SIN_MFA_TOTP_REQUIERE_CONFIGURACION",
            modulo="auth",
            tabla_afectada="core.usuarios",
            id_registro=usuario.id_usuario,
            detalle=f"Usuario {usuario.correo} inició sesión y debe configurar MFA con aplicación autenticadora.",
            nivel="INFO",
            resultado="PENDIENTE"
        )

        return {
            "message": "Login correcto. Debes configurar MFA con aplicación autenticadora.",
            "requiere_configurar_mfa": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id_usuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "estado": usuario.estado,
                "mfa_totp_enabled": usuario.mfa_totp_enabled
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# VERIFICAR 2FA
# =========================

@limiter.limit("5/minute")
@router.post("/verify-2fa")
def verify_2fa(
    data: Verificar2FA,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        usuario = db.query(Usuario).filter(
            Usuario.correo == data.correo
        ).first()

        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        if usuario.estado != "activo":
            raise HTTPException(
                status_code=403,
                detail="La cuenta no está activa."
            )

        codigo_db = (
            db.query(Codigo2FA)
            .filter(
                Codigo2FA.id_usuario == usuario.id_usuario,
                Codigo2FA.usado == False
            )
            .order_by(Codigo2FA.id_codigo.desc())
            .first()
        )

        if not codigo_db:
            raise HTTPException(
                status_code=400,
                detail="Código 2FA inválido"
            )

        if codigo_db.fecha_expiracion < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Código 2FA expirado"
            )

        if codigo_db.intentos >= 3:
            codigo_db.usado = True
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Código 2FA bloqueado por demasiados intentos"
            )

        if not verify_password(data.codigo, codigo_db.codigo):
            codigo_db.intentos += 1
            db.commit()
            registrar_auditoria(
                db=db,
                request=request,
                usuario=usuario,
                accion="LOGIN_2FA_CORREO_FALLIDO",
                modulo="auth",
                tabla_afectada="core.codigos_2fa",
                id_registro=codigo_db.id_codigo,
                detalle=f"Código 2FA incorrecto para {usuario.correo}. Intento {codigo_db.intentos} de 3.",
                nivel="WARNING",
                resultado="FALLIDO"
            )
            raise HTTPException(
                status_code=400,
                detail="Código 2FA inválido"
            )

        codigo_db.usado = True
        registrar_auditoria(
            db=db,
            request=request,
            usuario=usuario,
            accion="LOGIN_2FA_CORREO_EXITOSO",
            modulo="auth",
            tabla_afectada="core.codigos_2fa",
            id_registro=codigo_db.id_codigo,
            detalle=f"Usuario {usuario.correo} validó correctamente el código 2FA enviado por correo.",
            nivel="INFO",
            resultado="OK"
        )

        access_token = create_access_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario,
                "rol": usuario.rol
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario
            }
        )

        nueva_sesion = Sesion(
            id_usuario=usuario.id_usuario,
            token=access_token,
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            ),
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            activa=True
        )

        db.add(nueva_sesion)
        db.commit()

        return {
            "message": "2FA validado correctamente",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id_usuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "estado": usuario.estado
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# SOLO NEGOCIO
# =========================

@router.get("/solo-negocio")
def solo_negocio(user: Usuario = Depends(require_role("negocio"))):
    return {
        "message": "Bienvenido negocio",
        "usuario": user.nombre
    }


# =========================
# ADMIN - CAMBIAR ROL
# =========================

@router.patch("/usuarios/{id_usuario}/rol")
def cambiar_rol_usuario(
    id_usuario: int,
    datos: CambiarRolUsuario,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el superadministrador puede modificar roles"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    rol_anterior = usuario.rol
    usuario.rol = datos.nuevo_rol

    db.commit()
    db.refresh(usuario)
    registrar_auditoria(
        db=db,
        usuario=current_user,
        accion="ROL_USUARIO_CAMBIADO",
        modulo="usuarios",
        tabla_afectada="core.usuarios",
        id_registro=usuario.id_usuario,
        detalle=f"Superadmin {current_user.correo} cambió el rol del usuario {usuario.correo} de {rol_anterior} a {usuario.rol}.",
        nivel="WARNING",
        resultado="OK"
    )

    return {
        "message": "Rol actualizado correctamente",
        "id_usuario": usuario.id_usuario,
        "correo": usuario.correo,
        "nuevo_rol": usuario.rol
    }


# =========================
# ADMIN - CAMBIAR ESTADO USUARIO
# =========================

@router.patch("/usuarios/{id_usuario}/estado")
def cambiar_estado_usuario(
    id_usuario: int,
    datos: CambiarEstadoUsuario,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el superadministrador puede modificar estados de usuario"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if usuario.id_usuario == current_user.id_usuario and datos.nuevo_estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar, bloquear o dejar pendiente tu propio usuario superadmin"
        )

    proteger_unico_superadmin_activo(
        db=db,
        usuario=usuario,
        nuevo_estado=datos.nuevo_estado,
        accion="cambiar_estado"
    )

    if usuario.rol == "superadmin" and usuario.estado == "activo" and datos.nuevo_estado != "activo":
        total_superadmins_activos = db.query(Usuario).filter(
            Usuario.rol == "superadmin",
            Usuario.estado == "activo"
        ).count()

        if total_superadmins_activos <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el estado de este usuario porque es el único superadministrador activo del sistema"
            )

    estado_anterior = usuario.estado
    usuario.estado = datos.nuevo_estado

    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db=db,
        usuario=current_user,
        accion="ESTADO_USUARIO_CAMBIADO",
        modulo="usuarios",
        tabla_afectada="core.usuarios",
        id_registro=usuario.id_usuario,
        detalle=f"Superadmin {current_user.correo} cambió el estado del usuario {usuario.correo} de {estado_anterior} a {usuario.estado}.",
        nivel="WARNING",
        resultado="OK"
    )

    return {
        "message": "Estado actualizado correctamente",
        "id_usuario": usuario.id_usuario,
        "correo": usuario.correo,
        "estado_anterior": estado_anterior,
        "nuevo_estado": usuario.estado
    }



# =========================
# ADMIN - LISTAR USUARIOS
# =========================

@router.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el superadministrador puede listar usuarios"
        )

    usuarios = db.query(Usuario).all()

    return [
        {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "rol": usuario.rol,
            "estado": usuario.estado
        }
        for usuario in usuarios
    ]

# =========================
# ADMIN - ELIMINAR USUARIO
# =========================

@router.delete("/usuarios/{id_usuario}")
def eliminar_usuario_admin(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    from sqlalchemy import text

    if current_user.rol != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el superadministrador puede eliminar usuarios"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == id_usuario
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if usuario.id_usuario == current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario superadmin"
        )

    proteger_unico_superadmin_activo(
        db=db,
        usuario=usuario,
        accion="eliminar"
    )

    if usuario.rol == "superadmin" and usuario.estado == "activo":
        total_superadmins_activos = db.query(Usuario).filter(
            Usuario.rol == "superadmin",
            Usuario.estado == "activo"
        ).count()

        if total_superadmins_activos <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar este usuario porque es el único superadministrador activo del sistema"
            )

    correo_eliminado = usuario.correo
    rol_eliminado = usuario.rol

    try:
        # 1. Auditoría: no se elimina, se desvincula del usuario eliminado.
        db.execute(
            text("UPDATE core.auditoria SET id_usuario = NULL WHERE id_usuario = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 2. Citas del usuario como cliente.
        db.execute(
            text("""
                DELETE FROM core.carrito_detalle
                WHERE id_cita IN (
                    SELECT id_cita FROM core.citas WHERE id_cliente = :id_usuario
                )
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("""
                DELETE FROM core.detalle_cita
                WHERE id_cita IN (
                    SELECT id_cita FROM core.citas WHERE id_cliente = :id_usuario
                )
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("DELETE FROM core.citas WHERE id_cliente = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 3. Pedidos, pagos, facturas y detalles asociados al usuario.
        db.execute(
            text("""
                DELETE FROM core.pagos
                WHERE id_pedido IN (
                    SELECT id_pedido FROM core.pedidos WHERE id_usuario = :id_usuario
                )
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("""
                DELETE FROM core.facturas
                WHERE id_pedido IN (
                    SELECT id_pedido FROM core.pedidos WHERE id_usuario = :id_usuario
                )
                OR id_usuario = :id_usuario
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("""
                DELETE FROM core.pedido_detalle
                WHERE id_pedido IN (
                    SELECT id_pedido FROM core.pedidos WHERE id_usuario = :id_usuario
                )
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("DELETE FROM core.pedidos WHERE id_usuario = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 4. Calificaciones hechas por el usuario.
        db.execute(
            text("DELETE FROM core.calificaciones WHERE id_cliente = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 5. Carritos del usuario y sus detalles.
        db.execute(
            text("""
                DELETE FROM core.carrito_detalle
                WHERE id_carrito IN (
                    SELECT id_carrito FROM core.carritos WHERE id_usuario = :id_usuario
                )
            """),
            {"id_usuario": id_usuario}
        )

        db.execute(
            text("DELETE FROM core.carritos WHERE id_usuario = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 6. Tablas dependientes directas del usuario.
        db.execute(text("DELETE FROM core.codigos_2fa WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.verificacion_2fa WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.tokens_activacion WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.tokens_recuperacion WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.sesiones WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.usuario_rol WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.notificaciones WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})
        db.execute(text("DELETE FROM core.favoritos WHERE id_usuario = :id_usuario"), {"id_usuario": id_usuario})

        # 7. Negocios del usuario propietario.
        # Al borrar negocios, la BD debe eliminar en cascada servicios, empleados, productos,
        # citas, pedidos, favoritos, calificaciones, facturas, etc. asociados al negocio.
        db.execute(
            text("DELETE FROM core.negocios WHERE id_usuario_propietario = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        # 8. Usuario final.
        db.execute(
            text("DELETE FROM core.usuarios WHERE id_usuario = :id_usuario"),
            {"id_usuario": id_usuario}
        )

        registrar_auditoria(
            db=db,
            usuario=current_user,
            accion="USUARIO_ELIMINADO_TOTAL",
            modulo="usuarios",
            tabla_afectada="core.usuarios",
            id_registro=id_usuario,
            detalle=f"Superadmin {current_user.correo} eliminó totalmente el usuario {correo_eliminado} con rol {rol_eliminado}.",
            nivel="CRITICAL",
            resultado="OK"
        )

        db.commit()

        return {
            "message": "Usuario eliminado totalmente de la base de datos",
            "id_usuario": id_usuario,
            "correo": correo_eliminado
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo eliminar totalmente el usuario: {str(error)}"
        )


# =========================
# REFRESH TOKEN
# =========================

@router.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        token_type = payload.get("type")

        if token_type != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        correo = payload.get("sub")

        usuario = db.query(Usuario).filter(
            Usuario.correo == correo
        ).first()

        if not usuario:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        if usuario.estado != "activo":
            raise HTTPException(
                status_code=403,
                detail="La cuenta no está activa."
            )

        nuevo_access_token = create_access_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario,
                "rol": usuario.rol
            }
        )

        nueva_sesion = Sesion(
            id_usuario=usuario.id_usuario,
            token=nuevo_access_token,
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            ),
            activa=True
        )

        db.add(nueva_sesion)
        db.commit()

        return {
            "access_token": nuevo_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido"
        )


# =========================
# LOGOUT
# =========================

@router.post("/logout")
def logout(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token no enviado"
        )

    token_actual = auth_header.replace("Bearer ", "")

    sesion = db.query(Sesion).filter(
        Sesion.id_usuario == current_user.id_usuario,
        Sesion.token == token_actual,
        Sesion.activa == True
    ).first()

    if not sesion:
        raise HTTPException(
            status_code=401,
            detail="Sesión no encontrada o ya cerrada"
        )

    sesion.activa = False
    db.commit()
    registrar_auditoria(
        db=db,
        request=request,
        usuario=current_user,
        accion="LOGOUT",
        modulo="auth",
        tabla_afectada="core.sesiones",
        id_registro=sesion.id_sesion,
        detalle=f"Usuario {current_user.correo} cerró sesión correctamente.",
        nivel="INFO",
        resultado="OK"
    )
    return {
        "message": "Sesión cerrada correctamente"
    }
