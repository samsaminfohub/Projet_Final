import numpy as np
from typing import Dict, Any

def normalize_features(features: Dict[str, Any]) -> np.ndarray:
    """Normalize input features for ML model"""
    # Define normalization ranges
    ranges = {
        'sleep_hours': (0, 12),
        'exercise_hours': (0, 20),
        'stress_level': (1, 10),
        'social_activity': (1, 10),
        'work_hours': (0, 16),
        'screen_time': (0, 16)
    }
    
    normalized = []
    for key, (min_val, max_val) in ranges.items():
        value = features.get(key, 0)
        normalized_value = (value - min_val) / (max_val - min_val)
        normalized.append(max(0, min(1, normalized_value)))
    
    return np.array(normalized)

def interpret_risk_score(risk_score: float) -> str:
    """Convert risk score to human-readable level"""
    if risk_score < 0.3:
        return "Low Risk"
    elif risk_score < 0.6:
        return "Medium Risk"
    else:
        return "High Risk"