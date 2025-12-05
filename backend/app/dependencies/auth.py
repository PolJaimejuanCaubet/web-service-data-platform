from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.app.config.config import settings as env
from backend.app.dependencies.services import UserService, get_user_service
from backend.app.models.models_user import UserBase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_jwt_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, env.JWT_SECRET, algorithms=[env.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(
    payload: dict = Depends(get_current_jwt_payload), 
    service: UserService = Depends(get_user_service)
):
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await service.get_user_by_id(user_id) 
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserBase.model_validate(user)


def admin_required(user: UserBase = Depends(get_current_user)):
    
    if user.role != "admin": 
        raise HTTPException(status_code=403, detail="Admins only")
    return user


def owner_or_admin(target_user_id: str, current_user: UserBase = Depends(get_current_user)):
    
    if current_user.role == "admin": 
        return True
            
    if current_user.username != target_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
