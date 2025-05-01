from sqlalchemy import Column, Integer, String, Enum, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class UserType(str, enum.Enum):
    CUSTOMER = "customer"
    FREELANCER = "freelancer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)  
    first_name = Column(String, nullable=False)  
    last_name = Column(String, nullable=False)   
    patronymic = Column(String, nullable=True)   
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    created_at = Column(DateTime, default=func.now())  

    profile = relationship("Profile", back_populates="user", uselist=False)  # Добавляем связь

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, nullable=False)