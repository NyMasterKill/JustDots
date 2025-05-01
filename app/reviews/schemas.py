from pydantic import BaseModel, validator
from datetime import datetime

class ReviewBase(BaseModel):
    comment: str | None = None
    score: float

    @validator("score")
    def validate_score(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Score must be between 1 and 5")
        return v

class Review(ReviewBase):
    id: int
    user_id: int
    reviewer_id: int
    created_at: datetime

    class Config:
        from_attributes = True