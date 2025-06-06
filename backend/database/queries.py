from models import get_db_session
from sqlalchemy import or_

def get_all_movies(session):
    return session.query(Movie).all()

def search_movies(session, query):
    return session.query(Movie).filter(
        or_(
            Movie.title.ilike(f"%{query}%"),
            Movie.genres.ilike(f"%{query}%"),
            Movie.director.ilike(f"%{query}%")
        )
    ).all()

def get_movie_by_title(session, title):
    return session.query(Movie).filter(Movie.title == title).first()

def get_movies_by_ids(session, ids):
    return session.query(Movie).filter(Movie.id.in_(ids)).all()