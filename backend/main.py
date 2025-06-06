from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import database
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tasks")
def get_tasks(db: Session = Depends(database.SessionLocal)):
    return db.query(models.Task).all()