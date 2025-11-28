from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.app.config.config import settings as env
from backend.app.dependencies.services import UserService, get_user_service
from backend.app.models import UserBase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_jwt_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, env.JWT_SECRET, algorithms=[env.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(
    payload: dict = Depends(get_current_jwt_payload), 
    service: UserService = Depends(get_user_service)
):
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = service.get_user_by_id(user_id) 
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserBase.model_validate(user)


def admin_required(user: UserBase = Depends(get_current_user)):
    
    if user.role != "admin": 
        raise HTTPException(status_code=403, detail="Admins only")
    return user


def owner_or_admin(target_user_id: str, user: UserBase = Depends(get_current_user)):
    
    if user.role == "admin": 
        return True
    
    # Aquí tenemos un pequeño problema:
    # ¿Tiene tu modelo UserBase un campo '_id' para el ID de MongoDB?
    # Si UserBase solo tiene 'username', 'email', etc., este campo puede faltar.
    # Asumiendo que has añadido '_id' o 'user_id' a UserBase:
    if str(user._id) == target_user_id: # Usar str() si el _id de UserBase es un ObjectID o str
        return True
    
    # Alternativa si solo tienes el username en UserBase:
    if user.username == target_user_id: # Si target_user_id es el username
        raise HTTPException(status_code=403, detail="Not authorized")
