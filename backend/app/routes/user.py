from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UsuarioLogin
from app.utils.security import hash_password, verify_password

router = APIRouter()


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
            password_hash=hash_password(user.password)
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
                "correo": nuevo_usuario.correo
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login_user(user: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == user.correo).first()

        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if not verify_password(user.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        return {
            "message": "Login correcto",
            "usuario": {
                "id": usuario.id_usuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))