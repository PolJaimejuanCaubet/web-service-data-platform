from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from pymongo.collection import Collection
from backend.app.auth.jwt_utils import *
from backend.app.models.models_user import *
from backend.app.auth.hashing import hash_password, verify_password


class UserService:
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create_user(self, user_data: UserCreate):

        existing_user = await self.collection.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")

        user_dict = user_data.model_dump()
        user_dict["password"] = hash_password(user_data.password)
        user_dict["role"] = "standard_user"
        new_user = await self.collection.insert_one(user_dict)
        created_user = await self.collection.find_one({"_id": new_user.inserted_id})

        return created_user

    async def authenticate_user(self, username: str, password: str):

        user = await self.collection.find_one({"username": username})

        if not user:
            return None

        if not verify_password(password, user["password"]):
            return None

        return user

    async def get_user_by_id(self, user_id: str):
        _id = ObjectId(user_id)
        user = await self.collection.find_one({"_id": _id})
        user.pop("password", None)
        return user

    async def update_user(self, user_id: str, update_data: dict):

        _id = ObjectId(user_id)
        await self.collection.update_one({"_id": _id}, {"$set": update_data})
        return await self.get_user_by_id(user_id)

    async def delete_user(self, user_id: str):
        _id = ObjectId(user_id)

        user = await self.collection.find_one({"_id": _id})
        if not user:
            return None

        email = user["email"]
        full_name = user["full_name"]

        deletion_time = datetime.now(timezone.utc)
        result = await self.collection.delete_one({"_id": _id})
        if result.deleted_count == 0:
            return None

        return deletion_time, email, full_name

    async def get_all_users(self):

        user_list = []

        async for user in self.collection.find({"role": {"$ne": "admin"}}):
            user.pop("password", None)
            user["_id"] = str(user["_id"])
            user_list.append(user)

        return user_list

    async def update_role(self, user_id: str):

        _id = ObjectId(user_id)

        await self.collection.update_one({"_id": _id}, {"$set": {"role": "admin"}})

        return await self.get_user_by_id(user_id)
