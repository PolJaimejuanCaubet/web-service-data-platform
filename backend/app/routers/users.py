from fastapi import APIRouter, Depends, HTTPException
from backend.app.models import UserUpdate, UserBase
from backend.app.services.user_service import UserService
from backend.app.dependencies.services import *
from app.dependencies.auth import *
 

router = APIRouter(prefix="/users")

#pop password i refresh tokens is necessary ?

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    
    if not owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=403, 
            detail="You do not have permission to view this profile"
        )

    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user, dict):
        user.pop("password", None)
        user.pop("refresh_tokens", None)
    
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: str, 
    user_data: UserUpdate, 
    current_user: UserBase = Depends(get_current_user), 
    service: UserService = Depends(get_user_service)
):

    if not owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=403, 
            detail="Not owner of the account"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Invalid Input"
        )
        
    updated_user = service.update_user(user_id, update_data)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User updated",
            "user_id": user_id,
            "full_name": updated_user.full_name,
            "email": updated_user.email
            }
    
    
@router.delete("/{user_id}")
async def delete_user(
    user_id: str, 
    current_user: UserBase = Depends(get_current_user), 
    service: UserService = Depends(get_user_service)
):
    
    if not owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=403, 
            detail="Not owner of the profile"
        )
        
    deletion_time = service.delete_user(user_id)
    
    if deletion_time is None:
        raise HTTPException(status_code=404, detail="User not found or already deleted")
        
    return {
        "message": "User deleted successfully",
        "deleted_at": deletion_time.isoformat()
    }


@router.post("/revoke_sessions")
async def revoke_all_sessions(
    current_user: UserBase = Depends(get_current_user), 
    service: UserService = Depends(get_user_service)
):
    
    service.revoke_all_sessions(current_user._id)
    
    return {"message": "All sessions have been revoked. You must log in again."}


@router.get("")
async def get_all_users(
    current_user: UserBase = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    
    admin = admin_required(current_user)
    
    if admin is None:
        raise HTTPException(status_code=403, detail="User isn't the admin")
    
    admin = service.get_all_users(current_user.role)