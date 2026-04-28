import random
from datetime import datetime, timedelta

from app.models.codigo_2fa import Codigo2FA
from app.schemas.user import Verificar2FA
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.core.deps import require_role
from app.utils.email import enviar_codigo_email

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
            rol=user.rol
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

@router.post("/login")
def login_user(user: UsuarioLogin, db: Session = Depends(get_db)):
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

@router.post("/verify-2fa")
def verify_2fa(data: Verificar2FA, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == data.correo).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

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
            raise HTTPException(status_code=400, detail="Código 2FA inválido")

        if codigo_db.fecha_expiracion < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Código 2FA expirado")

        codigo_db.usado = True
        db.commit()

        access_token = create_access_token(
            data={
                "sub": usuario.correo,
                "id_usuario": usuario.id_usuario
            }
        )

        return {
            "message": "2FA validado correctamente",
            "access_token": access_token,
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
        raise HTTPException(status_code=500, detail=str(e))