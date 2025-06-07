import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
import joblib
import os

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the ML model"""
        try:
            # Try to load existing model
            if os.path.exists('model.joblib') and os.path.exists('scaler.joblib'):
                self.model = joblib.load('model.joblib')
                self.scaler = joblib.load('scaler.joblib')
            else:
                # Create and train a new model with synthetic data
                self._train_model()
        except Exception as e:
            print(f"Error initializing model: {e}")
            self._create_simple_model()
    
    def _train_model(self):
        """Train the model with synthetic data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: sleep_hours, exercise_hours, stress_level, social_activity, work_hours, screen_time
        data = {
            'sleep_hours': np.random.normal(7.5, 1.5, n_samples).clip(4, 12),
            'exercise_hours': np.random.exponential(3, n_samples).clip(0, 20),
            'stress_level': np.random.randint(1, 11, n_samples),
            'social_activity': np.random.randint(1, 11, n_samples),
            'work_hours': np.random.normal(8, 2, n_samples).clip(4, 16),
            'screen_time': np.random.normal(6, 3, n_samples).clip(1, 16)
        }
        
        X = pd.DataFrame(data)
        
        # Create target variable based on logical rules
        risk_scores = []
        for _, row in X.iterrows():
            score = 0
            # Poor sleep increases risk
            if row['sleep_hours'] < 6 or row['sleep_hours'] > 9:
                score += 0.3
            # Low exercise increases risk
            if row['exercise_hours'] < 2:
                score += 0.2
            # High stress increases risk
            score += (row['stress_level'] - 1) / 9 * 0.3
            # Low social activity increases risk
            score += (10 - row['social_activity']) / 9 * 0.2
            # Long work hours increase risk
            if row['work_hours'] > 10:
                score += 0.2
            # High screen time increases risk
            if row['screen_time'] > 8:
                score += 0.1
            
            risk_scores.append(min(score, 1.0))
        
        y = np.array(risk_scores)
        
        # Train scaler and model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Convert to classification problem
        y_class = (y > 0.5).astype(int)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_class)
        
        # Save model and scaler
        joblib.dump(self.model, 'model.joblib')
        joblib.dump(self.scaler, 'scaler.joblib')
    
    def _create_simple_model(self):
        """Create a simple rule-based model as fallback"""
        self.model = None
        self.scaler = None
    
    def predict(self, sleep_hours: float, exercise_hours: float, stress_level: int,
                social_activity: int, work_hours: float, screen_time: float) -> Tuple[float, str, List[str]]:
        """Make a prediction and return risk score, level, and recommendations"""
        
        # Prepare input data
        features = np.array([[sleep_hours, exercise_hours, stress_level, 
                            social_activity, work_hours, screen_time]])
        
        if self.model is not None and self.scaler is not None:
            # Use ML model
            features_scaled = self.scaler.transform(features)
            risk_prob = self.model.predict_proba(features_scaled)[0][1]
            risk_score = float(risk_prob)
        else:
            # Use rule-based approach
            risk_score = self._calculate_risk_score(
                sleep_hours, exercise_hours, stress_level,
                social_activity, work_hours, screen_time
            )
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "Low"
        elif risk_score < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sleep_hours, exercise_hours, stress_level,
            social_activity, work_hours, screen_time, risk_score
        )
        
        return risk_score, risk_level, recommendations
    
    def _calculate_risk_score(self, sleep_hours: float, exercise_hours: float,
                            stress_level: int, social_activity: int,
                            work_hours: float, screen_time: float) -> float:
        """Calculate risk score using rule-based approach"""
        score = 0.0
        
        # Sleep factor
        if sleep_hours < 6 or sleep_hours > 9:
            score += 0.25
        
        # Exercise factor
        if exercise_hours < 2:
            score += 0.2
        
        # Stress factor
        score += (stress_level - 1) / 9 * 0.3
        
        # Social activity factor
        score += (10 - social_activity) / 9 * 0.15
        
        # Work hours factor
        if work_hours > 10:
            score += 0.15
        
        # Screen time factor
        if screen_time > 8:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, sleep_hours: float, exercise_hours: float,
                                stress_level: int, social_activity: int,
                                work_hours: float, screen_time: float,
                                risk_score: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if sleep_hours < 7:
            recommendations.append("Try to get 7-9 hours of sleep per night for better mental health")
        elif sleep_hours > 9:
            recommendations.append("Excessive sleep might indicate underlying issues - consider consulting a healthcare provider")
        
        if exercise_hours < 2:
            recommendations.append("Aim for at least 2 hours of exercise per week to improve mood and reduce stress")
        
        if stress_level > 7:
            recommendations.append("Consider stress management techniques like meditation, deep breathing, or yoga")
        
        if social_activity < 5:
            recommendations.append("Try to increase social interactions - consider joining clubs or activities")
        
        if work_hours > 10:
            recommendations.append("Consider work-life balance - long work hours can negatively impact mental health")
        
        if screen_time > 8:
            recommendations.append("Reduce screen time, especially before bedtime, to improve sleep quality")
        
        if risk_score > 0.6:
            recommendations.append("Consider speaking with a mental health professional for additional support")
        
        if not recommendations:
            recommendations.append("Keep maintaining your healthy lifestyle habits!")
        
        return recommendations