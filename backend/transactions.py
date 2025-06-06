from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, TransactionCreate

router = APIRouter()

@router.post("/")
def add_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    new_tx = Transaction(**tx.dict())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()