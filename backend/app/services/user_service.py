from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException
from pymongo.collection import Collection
from backend.app.models import *
from backend.app.auth.hashing import hash_password, verify_password

class UserService:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create_user(self, user_data: UserCreate):
        if self.collection.find_one({"username": user_data.username}):
            raise HTTPException(status_code=409, detail="User already exists")

        user_dict = user_data.model_dump()
        user_dict["_id"] = str(uuid4())
        user_dict["password"] = hash_password(user_data.password)
        user_dict["refresh_tokens"] = []

        self.collection.insert_one(user_dict)
        
        return UserCreate.model_validate(user_dict)

    def authenticate_user(self, username: str, password: str):
        user_doc = self.collection.find_one({"username": username})
        
        if not user_doc:
            return None
        
        if not verify_password(password, user_doc["password"]):
            return None
            
        return UserBase.model_validate(user_doc)

    def add_refresh_token(self, user_id: str, token: str, expires_at: datetime):
        self.collection.update_one(
            {"_id": user_id},
            {"$push":
                {"refresh_tokens":
                    {"token": token, "expires_at": expires_at
                    }
                }
            }
        )

    def revoke_refresh_token(self, user_id: str, token: str):
        self.collection.update_one(
            {"_id": user_id},
            {"$pull":
                {"refresh_tokens":
                    {"token": token
                    }
                }
            }
        )
        
    def get_user_by_id(self, user_id: str):
        user = self.collection.find_one({"_id": user_id})
        if user:
            return UserBase.model_validate(user) 

        return None

    def update_user(self, user_id: str, update_data: dict):
        self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return self.get_user_by_id(user_id)


    def delete_user(self, user_id: str) -> Optional[datetime]:
        
        deletion_time = datetime.now(timezone.utc)
        result = self.collection.update_one(
            {"_id": user_id, "deleted_at": {"$exists": False}}, 
            {"$set": {"deleted_at": deletion_time}}
        )
        
        if result.matched_count == 0 and result.modified_count == 0:
            return None
            
        return deletion_time
    
    def revoke_all_sessions(self, user_id: str):
        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"refresh_tokens": []}}
        )