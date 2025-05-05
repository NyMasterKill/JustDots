from pydantic import BaseModel, EmailStr, validator
from .models import UserType
from typing import Optional
from ..users.schemas import Profile, Skill
from datetime import datetime
import re

class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    email: EmailStr
    password: str
    password_confirm: str
    user_type: UserType

    @validator("username")
    def validate_username(cls, v):
        # Регулярное выражение: только латинские буквы, цифры, подчёркивания, длина 3-50
        if not re.match(r"^[a-zA-Z0-9_]{3,50}$", v):
            raise ValueError(
                "Username должен содержать только латинские буквы, цифры и подчёркивания, "
                "без пробелов, длиной от 3 до 50 символов"
            )
        return v

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    patronymic: str | None
    email: EmailStr
    user_type: str
    created_at: str | None
    profile: Profile | None
    skills: list[Skill] = []
    rating: Optional[float] = None
    completed_tasks_count: int = 0

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str

    @validator("email", always=True)
    def check_credentials(cls, v, values, **kwargs):
        if not v and not values.get("username"):
            raise ValueError("Either email or username must be provided")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str