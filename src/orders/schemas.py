from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional

class OrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class OrderCreate(BaseModel):
    title: str
    description: str
    budget_from: float
    budget_to: float
    deadline: datetime
    category_id: int
    skills_text: str
    requirements: str

class OrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget_from: Optional[float] = None
    budget_to: Optional[float] = None
    deadline: Optional[datetime] = None
    category_id: Optional[int] = None
    skills_text: Optional[str] = None
    requirements: Optional[str] = None

class Order(BaseModel):
    id: int
    title: str
    description: str
    budget_from: float
    budget_to: float
    deadline: datetime
    customer_id: int
    executor_id: Optional[int] = None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    category_id: int
    skills_text: str
    requirements: str

    model_config = ConfigDict(
        from_attributes=True
    )