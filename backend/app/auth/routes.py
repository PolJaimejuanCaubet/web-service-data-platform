from backend.app.dependencies.services import get_user_service
from backend.app.models import UserCreate, UserLogin
from backend.app.database.database import users_collection
from backend.app.auth.hashing import *
from backend.app.auth.jwt_utils import *
from fastapi import APIRouter, Depends, HTTPException, Header
from uuid import uuid4
from typing import Optional
from datetime import datetime, timezone

from backend.app.services.user_service import UserService

router = APIRouter(prefix="/auth")

def add_refresh_token_to_user(user_id: str, token: str, expires_at: datetime):
    users_collection.update_one(
        {"_id": user_id},
        {"$push": 
            {"refresh_tokens": 
                {"token": token, 
                 "expires_at": expires_at
                }
            }
        }
    )

def remove_refresh_token_from_user(user_id: str, token: str):
    users_collection.update_one(
        {"_id": user_id},
        {"$pull":
            {"refresh_tokens":
                {"token": token
                }
            }
        }
    )

    
@router.post("/register")
def register(user: UserCreate, service: UserService = Depends(get_user_service)):
    
    new_user = service.create_user(user)
    
    return {
        "message": "User registered",
        "user_id": new_user["_id"],
        "role": new_user["role"]
    }


@router.post("/login")
def login(data: UserLogin, service: UserService = Depends(get_user_service)):
    
    user = service.authenticate_user(data.username, data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")


    token_data = {
        "user_id": user["_id"],
        "username": user["username"],
        "role": user["role"]
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    payload = decode_token(refresh_token)
    expires_at = None
    if payload and "exp" in payload:
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    service.add_refresh_token(user["_id"], refresh_token, expires_at)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": { 
            "id": user["_id"],
            "username": user["username"]
        }
    }


@router.post("/refresh")
def refresh_token(authorization: Optional[str] = Header(None), service: UserService = Depends(get_user_service)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    refresh_token = parts[1]
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Token is not of type 'refresh'")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid payload")

    is_valid = service.validate_refresh_token(user_id, refresh_token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid refresh token (not registered/revoked)")

    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = {
        "user_id": user_id,
        "username": user.username,
        "role": user.role
    }
    new_access = create_access_token(token_data)

    return {
        "access_token": new_access,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }
    


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None), service: UserService = Depends(get_user_service)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid payload")
    
    service.revoke_refresh_token(user_id, token)

    return {"message": "Logout successful"}
