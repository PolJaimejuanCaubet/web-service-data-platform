from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone

from fastapi.security import OAuth2PasswordRequestForm

from backend.app.database.database import get_db
from backend.app.models.models_user import UserCreate, UserLogin, UserResponse
from backend.app.auth.hashing import *
from backend.app.auth.jwt_utils import *

from backend.app.services.user_service import UserService
from backend.app.dependencies.services import get_user_service

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(user: UserCreate, service: UserService = Depends(get_user_service)):

    new_user = await service.create_user(user)

    return {
        "message": "User registered",
        "user_id": str(new_user["_id"]),
        "email": new_user["email"],
        "role": new_user["role"],
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):

    user = await db["users"].find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_tokenX(
        data={
            "user_id": str(user["_id"]),
            "username": user["username"],
            "role": user.get("role", "user"),
        },
        expires_delta=access_token_expires,
    )
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {"id": str(user["_id"]), "username": user["username"]},
    }


# NEED TO IMPLEMENT LOG OUT AND REFRESH

# @router.post("/refresh")
# async def refresh_token(
#     authorization: Optional[str] = Header(None),
#     service: UserService = Depends(get_user_service)
# ):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Missing Authorization header")

#     parts = authorization.split()
#     if len(parts) != 2 or parts[0].lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid Authorization header format")

#     refresh_token = parts[1]
#     payload = decode_token(refresh_token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

#     if payload.get("token_type") != "refresh":
#         raise HTTPException(status_code=401, detail="Token is not of type 'refresh'")

#     user_id = payload.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid payload")

#     is_valid = await service.validate_refresh_token(user_id, refresh_token)
#     if not is_valid:
#         raise HTTPException(status_code=401, detail="Invalid refresh token (not registered/revoked)")

#     user = await service.get_user_by_id(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     token_data = {
#         "user_id": str(user["_id"]),
#         "username": user["username"],
#         "role": user["role"]
#     }
#     new_access = create_access_token(token_data)

#     return {
#         "access_token": new_access,
#         "refresh_token": refresh_token,
#         "token_type": "Bearer",
#     }


# @router.post("/logout")
# def logout(
#     authorization: Optional[str] = Header(None),
#     service: UserService = Depends(get_user_service)
# ):

#     if not authorization:
#         raise HTTPException(status_code=401, detail="Missing Authorization header")

#     parts = authorization.split()
#     if len(parts) != 2 or parts[0].lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid Authorization header")

#     token = parts[1]

#     payload = decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

#     user_id = payload.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid payload")

#     service.revoke_refresh_token(user_id, token)

#     return {"message": "Logout successful"}
