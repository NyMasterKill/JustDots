from pydantic import BaseModel, validator, AnyUrl, TypeAdapter, ValidationError
from typing import List, Optional

class SkillBase(BaseModel):
    name: str

class Skill(SkillBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None

    @validator("url")
    def validate_url(cls, v):
        if v is None:
            return v
        try:
            url_adapter = TypeAdapter(AnyUrl)
            url_adapter.validate_python(v)
            return v
        except ValidationError:
            raise ValueError("Invalid URL format")

class Portfolio(PortfolioBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    bio: Optional[str] = None
    rating: float = 0.0

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    skills: Optional[List[SkillBase]] = None
    portfolio: Optional[List[PortfolioBase]] = None

class Profile(ProfileBase):
    user_id: int
    portfolio: List[Portfolio] = []

    class Config:
        from_attributes = True