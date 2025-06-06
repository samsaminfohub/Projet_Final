from fastapi import FastAPI
from auth import router as auth_router
from transactions import router as transactions_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(transactions_router, prefix="/transactions")