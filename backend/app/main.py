from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from models.database import engine, SessionLocal, Base
from routes import predictions, auth
from services.ml_service import MLService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mental Health Predictor API",
    description="API for predicting mental health risks based on lifestyle factors",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML service
ml_service = MLService()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Mental Health Predictor API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
