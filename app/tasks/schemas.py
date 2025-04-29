from pydantic import BaseModel
from typing import Optional


CATEGORIES = ["Разработка", "Дизайн", "Программирование", "Копирайтинг", "Другое"]
REQUIREMENTS = ["Базовый", "Средний", "Продвинутый"]
STATUSES = ["Открытая", "Закрытая", "В процессе"]


class TaskCreate(BaseModel):
    title: str
    description: str
    budget_from: str
    budget_to: str
    category: str
    requirements: str
    deadline: Optional[str] = None
    status: str = "Открытая"


class TaskResponse(TaskCreate):
    id: int
    owner_id: int

    class Config:
        from_attributes = True