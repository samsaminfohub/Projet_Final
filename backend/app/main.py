from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Charger le modèle ML
model = joblib.load("model.pkl")

class InputData(BaseModel):
    feature1: float
    feature2: float

@app.post("/predict/")
def predict(data: InputData):
    try:
        df = pd.DataFrame([data.dict().values()], columns=data.dict().keys())
        prediction = model.predict(df)
        return {"prediction": prediction[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
