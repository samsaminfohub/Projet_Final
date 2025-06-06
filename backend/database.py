import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@db/budgetdb"

# Retry logic to wait for PostgreSQL
for _ in range(10):
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        connection = engine.connect()
        connection.close()
        break
    except Exception as e:
        print("Database not ready, waiting...")
        time.sleep(3)
else:
    raise RuntimeError("Could not connect to database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()