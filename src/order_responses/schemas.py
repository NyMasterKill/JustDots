from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class OrderResponseCreate(BaseModel):
    order_id: int
    proposed_price: float
    comment: str

class OrderResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    proposed_price: float
    comment: str
    status: ResponseStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )