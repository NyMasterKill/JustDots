from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime
import enum

class OrderStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    budget_from = Column(Float, nullable=False)
    budget_to = Column(Float, nullable=False)
    deadline = Column(DateTime, nullable=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    skills_text = Column(Text)
    requirements = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(OrderStatus), default=OrderStatus.OPEN)
    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders_created")
    executor = relationship("User", foreign_keys=[executor_id], back_populates="orders_executed")
    category = relationship("Category", back_populates="orders")
    responses = relationship("OrderResponse", back_populates="order")