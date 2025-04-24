from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    avatar_url = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    rating = Column(Float, default=0.0)  
    created_at = Column(DateTime, default=datetime.utcnow)
    role = relationship("Role", back_populates="users")
    skills = relationship("UserSkill", back_populates="user")
    portfolio = relationship("UserPortfolio", back_populates="portfolio")
    reviews_authored = relationship("Review", foreign_keys="Review.author_id", back_populates="author")
    reviews_received = relationship("Review", foreign_keys="Review.target_id", back_populates="target")
    orders_created = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    orders_executed = relationship("Order", foreign_keys="Order.executor_id", back_populates="executor")
    responses = relationship("OrderResponse", back_populates="user")