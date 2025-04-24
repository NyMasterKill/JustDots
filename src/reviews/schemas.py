from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    order_id: int
    target_id: int
    rating: float
    comment: Optional[str] = None

class Review(BaseModel):
    id: int
    author_id: int
    target_id: int
    rating: float
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )