from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.database import get_db
from models.mental_health import Prediction
from services.ml_service import MLService
from services.database_service import DatabaseService

router = APIRouter()

class PredictionRequest(BaseModel):
    sleep_hours: float
    exercise_hours: float
    stress_level: int
    social_activity: int
    work_hours: float
    screen_time: float
    user_id: Optional[int] = None

class PredictionResponse(BaseModel):
    id: int
    risk_score: float
    risk_level: str
    recommendations: List[str]
    prediction_date: datetime

@router.post("/predict", response_model=PredictionResponse)
async def predict_mental_health(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    try:
        # Initialize services
        ml_service = MLService()
        db_service = DatabaseService(db)
        
        # Make prediction
        risk_score, risk_level, recommendations = ml_service.predict(
            sleep_hours=request.sleep_hours,
            exercise_hours=request.exercise_hours,
            stress_level=request.stress_level,
            social_activity=request.social_activity,
            work_hours=request.work_hours,
            screen_time=request.screen_time
        )
        
        # Save prediction to database
        prediction = db_service.save_prediction(
            user_id=request.user_id,
            sleep_hours=request.sleep_hours,
            exercise_hours=request.exercise_hours,
            stress_level=request.stress_level,
            social_activity=request.social_activity,
            work_hours=request.work_hours,
            screen_time=request.screen_time,
            risk_score=risk_score,
            risk_level=risk_level
        )
        
        return PredictionResponse(
            id=prediction.id,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
            prediction_date=prediction.prediction_date
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions(
    limit: int = 10,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        db_service = DatabaseService(db)
        predictions = db_service.get_predictions(user_id=user_id, limit=limit)
        
        return [
            PredictionResponse(
                id=p.id,
                risk_score=p.risk_score,
                risk_level=p.risk_level,
                recommendations=[],  # Add recommendations logic if needed
                prediction_date=p.prediction_date
            )
            for p in predictions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))