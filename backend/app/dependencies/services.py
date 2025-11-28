from fastapi import Depends
from backend.app.database import get_collection
from backend.app.services.user_service import UserService

def get_user_service(collection = Depends(get_collection)):
    return UserService(collection)