from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кому отзыв
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кто оставил отзыв
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    comment = Column(Text, nullable=True)
    score = Column(Float, nullable=False)  # Оценка от 1 до 5
    created_at = Column(DateTime, default=func.now())

    # Связи
    user = relationship("User", backref="reviews", foreign_keys=[user_id])
    reviewer = relationship("User", backref="reviews_written", foreign_keys=[reviewer_id])
    task = relationship("Task", backref="reviews")