from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional

from ..models.mental_health import User, Prediction

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def create_user(self, username: str, email: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def save_prediction(self, user_id: Optional[int], sleep_hours: float,
                       exercise_hours: float, stress_level: int,
                       social_activity: int, work_hours: float,
                       screen_time: float, risk_score: float,
                       risk_level: str) -> Prediction:
        prediction = Prediction(
            user_id=user_id,
            sleep_hours=sleep_hours,
            exercise_hours=exercise_hours,
            stress_level=stress_level,
            social_activity=social_activity,
            work_hours=work_hours,
            screen_time=screen_time,
            risk_score=risk_score,
            risk_level=risk_level
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction
    
    def get_predictions(self, user_id: Optional[int] = None, limit: int = 10) -> List[Prediction]:
        query = self.db.query(Prediction)
        if user_id:
            query = query.filter(Prediction.user_id == user_id)
        return query.order_by(Prediction.prediction_date.desc()).limit(limit).all()