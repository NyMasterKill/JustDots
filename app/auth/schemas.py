from pydantic import BaseModel, EmailStr, validator
from .models import UserType
from ..users.schemas import Profile, Skill  # Импортируем Skill

class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    email: EmailStr
    password: str
    password_confirm: str
    user_type: UserType

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
    profile: Profile | None  # Делаем profile опциональным
    skills: list[Skill] = []  # Добавляем skills

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