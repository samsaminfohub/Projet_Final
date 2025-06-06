import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import mlflow
import mlflow.sklearn
from database.models import get_db_session
from database.queries import get_all_movies
import os

def train_recommendation_model(db_url):
    # Récupérer les données depuis la base de données
    session = get_db_session(db_url)
    movies = get_all_movies(session)
    df = pd.DataFrame([(m.id, m.title, m.genres, m.overview) for m in movies], 
                      columns=['id', 'title', 'genres', 'overview'])
    
    # Créer une colonne de metadata pour le modèle
    df['metadata'] = df.apply(lambda x: f"{x['genres']} {x['overview']}", axis=1)
    
    # Vectorisation TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['metadata'])
    
    # Calcul de similarité cosinus
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # Enregistrement du modèle avec MLflow
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    mlflow.set_experiment("MovieRecommender")
    
    with mlflow.start_run():
        mlflow.log_param("dataset_size", len(df))
        mlflow.log_param("vectorizer", "TF-IDF")
        mlflow.sklearn.log_model(tfidf, "tfidf_vectorizer")
        mlflow.log_artifact(local_path="data/movies.csv", artifact_path="data")
        
        # Enregistrer les indices pour la recommandation
        indices = pd.Series(df.index, index=df['title']).to_dict()
        mlflow.log_dict(indices, "indices.json")
        
        # Enregistrer la matrice de similarité
        import tempfile
        import numpy as np
        
        with tempfile.NamedTemporaryFile(suffix='.npy') as tmp:
            np.save(tmp.name, cosine_sim)
            mlflow.log_artifact(tmp.name, "similarity_matrix")
    
    return df, indices, cosine_sim