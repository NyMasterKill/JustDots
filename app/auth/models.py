from sqlalchemy import Column, Integer, String, Enum, Text
from ..database import Base
import enum

class UserType(enum.Enum):
    CUSTOMER = "CUSTOMER"
    FREELANCER = "FREELANCER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, nullable=False)