from fastapi import APIRouter, Depends, HTTPException
from backend.app.models.models_user import UserUpdate, UserBase
from backend.app.services.user_service import UserService
from backend.app.dependencies.services import *
from backend.app.dependencies.auth import *

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):

    if not owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=403, detail="You do not have permission to view this profile"
        )

    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    user.pop("password", None)

    return user


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):

    if not owner_or_admin(user_id, current_user):
        raise HTTPException(status_code=403, detail="Not owner of the account")

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Invalid Input")

    updated_user = await service.update_user(user_id, update_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "User updated",
        "user_id": user_id,
        "full_name": updated_user["full_name"],
        "email": updated_user["email"],
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):

    if not owner_or_admin(user_id, current_user):
        raise HTTPException(status_code=403, detail="Not owner of the profile")

    result = await service.delete_user(user_id)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    deletion_time, email, full_name = result

    return {
        "message": "User deleted successfully",
        "full_name": full_name,
        "email": email,
        "deleted_at": deletion_time.isoformat(),
    }


@router.get("")
async def get_all_users(
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):

    admin_required(current_user)

    list_of_users = await service.get_all_users()

    return {"list_of_users": list_of_users}


@router.put("/{user_id}/role")
async def update_role(
    user_id: str,
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):

    admin_required(current_user)
    user = await service.update_role(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"role": f"User with _id {user_id} now has new role - {user["role"]}"}
