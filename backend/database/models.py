from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    genres = Column(String(200))
    year = Column(Integer)
    rating = Column(Float)
    overview = Column(Text)
    director = Column(String(100))
    actors = Column(Text)
    
    def __repr__(self):
        return f"<Movie(title='{self.title}', year={self.year})>"

def get_db_session(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()