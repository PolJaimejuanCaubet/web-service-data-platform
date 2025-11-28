from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
