from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import crud, models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/tasks/")
def create_task(task: models.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)