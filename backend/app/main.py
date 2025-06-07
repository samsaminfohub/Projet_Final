from fastapi import FastAPI
from pydantic import BaseModel
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

app = FastAPI()

MODEL_PATH = "model.pkl"

# Schéma de la requête
class Features(BaseModel):
    feature1: float
    feature2: float

# Entraînement automatique si le modèle n’existe pas
def train_and_save_model():
    X, y = make_classification(n_samples=1000, n_features=2, n_informative=2,
                               n_redundant=0, random_state=42)
    df = pd.DataFrame(X, columns=["feature1", "feature2"])
    df["target"] = y
    X_train, _, y_train, _ = train_test_split(df[["feature1", "feature2"]],
                                              df["target"], test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    print("✅ Modèle entraîné et sauvegardé.")
    return model

# Chargement ou entraînement du modèle
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ Modèle chargé depuis model.pkl")
else:
    model = train_and_save_model()

# Endpoint de prédiction
@app.post("/predict/")
def predict(features: Features):
    data = [[features.feature1, features.feature2]]
    prediction = model.predict(data)
    return {"prediction": int(prediction[0])}
