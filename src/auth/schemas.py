from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    login: str
    password: str
    role_id: int

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        alias={"username": "email"}
    )

class Token(BaseModel):
    access_token: str
    token_type: str

class UserSkillSchema(BaseModel):
    skill_id: int
    skill_name: str

    model_config = ConfigDict(
        from_attributes=True
    )

class UserPortfolioSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class UserProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    login: str
    avatar_url: Optional[str] = None
    role_id: int
    rating: float
    created_at: datetime
    skills: List[UserSkillSchema] = []
    portfolio: List[UserPortfolioSchema] = []

    model_config = ConfigDict(
        from_attributes=True
    )

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    avatar_url: Optional[str] = None