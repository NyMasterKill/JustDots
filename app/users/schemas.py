from pydantic import BaseModel, validator
from typing import List
from pydantic.networks import AnyUrl
from pydantic_core import PydanticCustomError
from pydantic import TypeAdapter
from fastapi import UploadFile

class SkillBase(BaseModel):
    name: str

class Skill(SkillBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    title: str
    description: str | None = None
    url: str | None = None

    @validator("url")
    def validate_url(cls, v):
        if v is None:
            return v
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        try:
            url_adapter = TypeAdapter(AnyUrl)
            url_adapter.validate_python(v)
            return v
        except PydanticCustomError:
            raise ValueError("Invalid URL format")

class Portfolio(PortfolioBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    bio: str | None = None
    rating: float | None = None
    avatar_url: str | None = None  # Добавляем avatar_url

class Profile(ProfileBase):
    user_id: int
    portfolio: List[Portfolio] = []

    class Config:
        from_attributes = True

class SkillCreate(BaseModel):
    name: str

class PortfolioCreate(BaseModel):
    title: str
    description: str | None = None
    url: str | None = None

class ProfileUpdate(BaseModel):
    bio: str | None = None
    rating: float | None = None
    skills: List[SkillCreate] | None = None
    portfolio: List[PortfolioCreate] | None = None
    avatar: UploadFile | None = None  # Добавляем поддержку загрузки файла