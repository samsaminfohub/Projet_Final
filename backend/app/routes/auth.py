from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from ..models.database import get_db
from ..models.mental_health import User
from ..services.database_service import DatabaseService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_service = DatabaseService(db)
        
        # Check if user exists
        if db_service.get_user_by_email(user.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        if db_service.get_user_by_username(user.username):
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        
        # Create user
        new_user = db_service.create_user(
            username=user.username,
            email=user.email,
            password=user.password
        )
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Simple token response for demo purposes
    # In production, implement proper JWT authentication
    return {"access_token": "demo_token", "token_type": "bearer"}