# backend/app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, models

app = FastAPI()

# Database models would be defined in database.py

@app.get("/")
def read_root():
    return {"message": "Welcome to MiniLab2 API"}

@app.get("/data/")
def get_all_data(db: Session = Depends(database.get_db)):
    data = db.query(models.LabData).all()
    return data

@app.post("/data/")
def create_data(data: dict, db: Session = Depends(database.get_db)):
    # Add data creation logic here
    return {"message": "Data created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
                        