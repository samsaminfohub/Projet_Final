from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None

class Book(BookCreate):
    id: int

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    book_id: int
    comment: str
    rating: int

class Comment(CommentCreate):
    id: int

    class Config:
        orm_mode = True

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/books/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Book).offset(skip).limit(limit).all()

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/comments/", response_model=Comment)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == comment.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found for comment")
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/comments/{book_id}", response_model=List[Comment])
def read_comments(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.book_id == book_id).all()
