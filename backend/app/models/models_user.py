from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserBase(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    role: str = "standard_user"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    
class UserResponse(UserBase):
    # Map MongoDB's '_id' to 'id' in the JSON response
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    role: str

    class Config:
        populate_by_name = True
        from_attributes = True
