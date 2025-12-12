from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException
from backend.app.auth.jwt_utils import *
from backend.app.models.models_user import *
from backend.app.auth.hashing import hash_password, verify_password
from backend.app.models.mongo_logger import MongoLogger


class UserService:
    def __init__(self, collection, log_collection: MongoLogger):
        self.collection = collection
        self._log_collection = log_collection

    async def create_user(self, user_data: UserCreate):
        try:
            existing_user = await self.collection.find_one(
                {"username": user_data.username}
            )
            if existing_user:
                await self._log_collection.log(
                    service="UserService",
                    status="error",
                    message="User already exists",
                    metadata={"username": user_data.username},
                )
                raise HTTPException(status_code=409, detail="User already exists")

            user_dict = user_data.model_dump()
            user_dict["password"] = hash_password(user_data.password)
            user_dict["role"] = "standard_user"
            new_user = await self.collection.insert_one(user_dict)
            created_user = await self.collection.find_one({"_id": new_user.inserted_id})

            await self._log_collection.log(
                service="UserService",
                status="success",
                message="User has been created succesfully",
                metadata=user_dict,
            )

            return created_user
        except Exception as e:
            await self._log_collection.log(
                service="UserService", status="error", message="User not created"
            )
            raise e

    async def login_user(self, user):
        try:
            authenticated_user = await self.collection.find_one(
                {"username": user.username}
            )

            if not authenticated_user or not verify_password(
                user.password, authenticated_user["password"]
            ):
                await self._log_collection.log(
                    service="UserService",
                    status="warning",
                    message="Login failed: Incorrect username or password",
                    metadata={"username": user.username},
                )
                raise HTTPException(
                    status_code=403, detail="Incorrect username or password"
                )

            access_token_expires = timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_tokenX(
                data={
                    "user_id": str(authenticated_user["_id"]),
                    "username": authenticated_user["username"],
                    "role": authenticated_user.get("role", "user"),
                },
                expires_delta=access_token_expires,
            )

            await self._log_collection.log(
                service="UserService",
                status="success",
                message="User logged in successfully",
                metadata={"username": user.username},
            )
            return authenticated_user, access_token

        except Exception as e:
            if not isinstance(e, HTTPException):
                await self._log_collection.log(
                    service="UserService",
                    status="error",
                    message="Login error",
                    metadata={"error": str(e)},
                )
            raise e

    async def get_user_by_id(self, user_id: str):
        _id = ObjectId(user_id)
        user = await self.collection.find_one({"_id": _id})
        user.pop("password", None)
        return user

    async def update_user(self, user_id: str, update_data: dict):
        try:
            _id = ObjectId(user_id)
            await self.collection.update_one({"_id": _id}, {"$set": update_data})

            updated_user = await self.get_user_by_id(user_id)

            await self._log_collection.log(
                service="UserService",
                status="success",
                message="User updated successfully",
                metadata={
                    "user_id": user_id,
                    "updated_fields": list(update_data.keys()),
                },
            )
            return updated_user
        except Exception as e:
            await self._log_collection.log(
                service="UserService",
                status="error",
                message="Error updating user",
                metadata={"user_id": user_id, "error": str(e)},
            )
            raise e

    async def delete_user(self, user_id: str):
        try:
            _id = ObjectId(user_id)

            user = await self.collection.find_one({"_id": _id})
            if not user:
                await self._log_collection.log(
                    service="UserService",
                    status="error",
                    message="User doesn't exist, cannot be deleted",
                    metadata={
                        "user_id": user_id,
                    },
                )
                return None

            email = user["email"]
            full_name = user["full_name"]

            deletion_time = datetime.now(timezone.utc)
            result = await self.collection.delete_one({"_id": _id})
            if result.deleted_count == 0:
                return None

            await self._log_collection.log(
                service="UserService",
                status="success",
                message="User deleted successfully",
                metadata={"user_id": user_id},
            )

            return deletion_time, email, full_name
        except Exception as e:
            await self._log_collection.log(
                service="UserService",
                status="error",
                message="Error deleting user",
                metadata={"user_id": user_id, "error": str(e)},
            )
            raise e

    async def get_all_users(self):

        user_list = []

        async for user in self.collection.find({"role": {"$ne": "admin"}}):
            user.pop("password", None)
            user["_id"] = str(user["_id"])
            user_list.append(user)

        return user_list

    async def update_role(self, user_id: str):
        try:
            _id = ObjectId(user_id)

            await self.collection.update_one({"_id": _id}, {"$set": {"role": "admin"}})
            await self._log_collection.log(
                service="UserService",
                status="success",
                message="User updated to admin role successfully",
                metadata={"user_id": user_id},
            )
            return await self.get_user_by_id(user_id)
        except Exception as e:
            await self._log_collection.log(
                service="UserService",
                status="error",
                message="Error updating role user",
                metadata={"user_id": user_id, "error": str(e)},
            )
            raise e
