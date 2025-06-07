from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Anonymous predictions allowed
    sleep_hours = Column(Float, nullable=False)
    exercise_hours = Column(Float, nullable=False)
    stress_level = Column(Integer, nullable=False)
    social_activity = Column(Integer, nullable=False)
    work_hours = Column(Float, nullable=False)
    screen_time = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())