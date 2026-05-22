import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.user import CambiarRolUsuario
from app.security.dependencies import get_current_user
from app.core.deps import get_current_user, require_role
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.codigo_2fa import Codigo2FA
from app.models.sesion import Sesion
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioLogin, Verificar2FA
from app.utils.email import enviar_codigo_email
from app.utils.security import (
    SECRET_KEY,
    ALGORITHM,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter()

@router.get("/me")
def get_me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id_usuario,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "correo": current_user.correo,
        "rol": current_user.rol
    }


@router.post("/register", status_code=201)
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        existente = db.query(Usuario).filter(Usuario.correo == user.correo).first()

        if existente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

        nuevo_usuario = Usuario(
            nombre=user.nombre,
            apellido=user.apellido,
            correo=user.correo,
            telefono=user.telefono,
            password_hash=hash_password(user.password),
            rol="cliente",
            estado="pendiente"
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        return {
            "message": "Usuario creado correctamente",
            "usuario": {
                "id": nuevo_usuario.id_usuario,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
                "rol": nuevo_usuario.rol
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/solo-negocio")
def solo_negocio(user: Usuario = Depends(require_role("negocio"))):
    return {
        "message": "Bienvenido negocio",
        "usuario": user.nombre
    }

@limiter.limit("5/minute")
@router.post("/login")
def login_user(
    request: Request,
    user: UsuarioLogin,
    db: Session = Depends(get_db)
):
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()

        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not verify_password(user.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        codigo = str(random.randint(100000, 999999))

        nuevo_codigo = Codigo2FA(
            id_usuario=usuario.id_usuario,
            codigo=codigo,
            fecha_expiracion=datetime.utcnow() + timedelta(minutes=5),
            usado=False
        )

        db.add(nuevo_codigo)
        db.commit()

        enviar_codigo_email(usuario.correo, codigo)

        return {
            "message": "Código 2FA enviado al correo",
            "requieres_2fa": True,
            "correo": usuario.correo
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

        codigo_db = (
            db.query(Codigo2FA)
            .filter(
                Codigo2FA.id_usuario == usuario.id_usuario,
                Codigo2FA.codigo == data.codigo,
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

        codigo_db.usado = True

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
                "rol": usuario.rol
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

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.rol = datos.nuevo_rol

    db.commit()
    db.refresh(usuario)

    return {
        "message": "Rol actualizado correctamente",
        "id_usuario": usuario.id_usuario,
        "correo": usuario.correo,
        "nuevo_rol": usuario.rol
    }

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

    return {
        "message": "Sesión cerrada correctamente"
    }