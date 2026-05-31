from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Usuario
from app.models.sesion import Sesion
from app.utils.security import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")

        if correo is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    usuario = db.query(Usuario).filter(
        Usuario.correo == correo
    ).first()

    if usuario is None:
        raise credentials_exception

    sesion = db.query(Sesion).filter(
        Sesion.token == token,
        Sesion.activa == True
    ).first()

    if not sesion:
        raise credentials_exception

    return usuario


def require_role(role: str):
    def role_dependency(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol == "superadmin":
            return current_user

        if current_user.rol != role:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Se requiere rol: {role}"
            )

        return current_user

    return role_dependency

def require_roles(roles: list[str]):
    def roles_dependency(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol == "superadmin":
            return current_user

        if current_user.rol not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Roles permitidos: {roles}"
            )

        return current_user

    return roles_dependency
