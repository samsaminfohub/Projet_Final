from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class UserCreate(BaseModel):
    email: str
    password: str

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # income or expense
    category = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TransactionCreate(BaseModel):
    type: str
    category: str
    amount: float