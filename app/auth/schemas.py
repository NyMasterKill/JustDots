from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_type: Literal["customer", "freelancer"]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str