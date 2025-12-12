from fastapi import APIRouter, Depends

from fastapi.security import OAuth2PasswordRequestForm
from backend.app.auth.hashing import *
from backend.app.auth.jwt_utils import *

from backend.app.models.models_user import UserCreate
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
async def login(
    user: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):

    authenticated_user, access_token = await service.login_user(user)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {
            "id": str(authenticated_user["_id"]),
            "username": authenticated_user["username"],
        },
    }


# NEED TO IMPLEMENT LOG OUT AND REFRESH
