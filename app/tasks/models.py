from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


# Перечисления для полей задачи
CATEGORIES = ["Разработка", "Дизайн", "Программирование", "Копирайтинг", "Другое"]
REQUIREMENTS = ["Базовый", "Средний", "Продвинутый"]
STATUSES = ["Открытая", "Закрытая", "В процессе"]

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    budget_from = Column(String)
    budget_to = Column(String)
    deadline = Column(String, nullable=True)
    category = Column(String)
    requirements = Column(String)
    status = Column(String)

    # Привязка к пользователю
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")