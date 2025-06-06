import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from database.models import get_db_session
from database.queries import get_all_movies

def preprocess_data(session):
    movies = get_all_movies(session)
    df = pd.DataFrame([(m.id, m.title, m.genres, m.overview) for m in movies], 
                     columns=['id', 'title', 'genres', 'overview'])
    
    # Nettoyage des données
    df['overview'] = df['overview'].fillna('')
    df['genres'] = df['genres'].fillna('')
    
    # Création de metadata pour le modèle
    df['metadata'] = df.apply(lambda x: f"{x['genres']} {x['overview']}", axis=1)
    
    return df

def compute_similarity_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['metadata'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim