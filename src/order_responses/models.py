from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime
import enum

class ResponseStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class OrderResponse(Base):
    __tablename__ = "order_responses"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ResponseStatus), default=ResponseStatus.PENDING, nullable=False)
    comment = Column(Text, nullable=False)
    proposed_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    order = relationship("Order", back_populates="responses")
    user = relationship("User", back_populates="responses")