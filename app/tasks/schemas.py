from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    OPEN = "Открытая"
    IN_PROGRESS = "В процессе"
    CLOSED = "Закрытая"


class TaskSkillLevel(str, Enum):
    BASIC = "Базовый"
    MEDIUM = "Средний"
    ADVANCED = "Продвинутый"


class TaskCategory(str, Enum):
    DEVELOPMENT = "Разработка"
    DESIGN = "Дизайн"
    PROGRAMMING = "Программирование"
    COPYWRITING = "Копирайтинг"
    OTHER = "Другое"


# Для создания задачи
class TaskCreate(BaseModel):
    title: str
    description: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[datetime] = None  # Меняем с str на datetime
    category: TaskCategory
    custom_category: Optional[str] = None
    skill_level: TaskSkillLevel

    model_config = {"use_enum_values": True, "from_attributes": True}


# Для обновления задачи
class TaskUpdate(TaskCreate):
    title: Optional[str] = None
    description: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[datetime] = None  # Меняем с str на datetime
    category: Optional[TaskCategory] = None
    custom_category: Optional[str] = None
    skill_level: Optional[TaskSkillLevel] = None
    status: Optional[TaskStatus] = None


# Ответ при получении задачи
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    budget_min: Optional[float]
    budget_max: Optional[float]
    deadline: Optional[datetime]  # Меняем с str на datetime
    category: TaskCategory
    custom_category: Optional[str]
    skill_level: TaskSkillLevel
    status: TaskStatus

    model_config = {"use_enum_values": True, "from_attributes": True}