from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(req: PredictRequest):
    # Exemple basique de prédiction (à remplacer par ton modèle ML)
    prediction = "positive" if "happy" in req.text.lower() else "negative"
    return {"prediction": prediction}
