from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.models import get_db_session
from database.queries import get_all_movies, search_movies, get_movie_by_title
from ml.recommender import MovieRecommender
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du recommandeur
recommender = MovieRecommender(os.getenv("DATABASE_URL"))

@app.get("/movies")
async def list_movies(query: str = None):
    session = get_db_session(os.getenv("DATABASE_URL"))
    if query:
        movies = search_movies(session, query)
    else:
        movies = get_all_movies(session)
    session.close()
    
    return [{
        'id': m.id,
        'title': m.title,
        'year': m.year,
        'genres': m.genres,
        'rating': m.rating,
        'overview': m.overview
    } for m in movies]

@app.post("/recommend")
async def recommend_movies(movie_title: str, top_n: int = 5):
    recommendations = recommender.recommend(movie_title, top_n)
    return recommendations

@app.get("/movies/{movie_id}")
async def get_movie(movie_id: int):
    session = get_db_session(os.getenv("DATABASE_URL"))
    movie = session.query(Movie).filter(Movie.id == movie_id).first()
    session.close()
    
    if movie:
        return {
            'id': movie.id,
            'title': movie.title,
            'year': movie.year,
            'genres': movie.genres,
            'rating': movie.rating,
            'overview': movie.overview,
            'director': movie.director,
            'actors': movie.actors
        }
    return {"error": "Movie not found"}, 404