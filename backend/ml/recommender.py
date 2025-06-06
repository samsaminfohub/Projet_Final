import numpy as np
import pandas as pd
import mlflow
import json
from database.queries import get_movies_by_ids

class MovieRecommender:
    def __init__(self, db_url):
        self.db_url = db_url
        self.load_model()
    
    def load_model(self):
        # Charger le modèle depuis MLflow
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=["1"],  # ID de l'expérience MovieRecommender
            order_by=["attributes.start_time DESC"],
            max_results=1
        )
        
        if runs:
            latest_run = runs[0]
            run_id = latest_run.info.run_id
            
            # Charger les artefacts
            self.indices = mlflow.artifacts.load_dict(f"runs:/{run_id}/indices.json")
            
            # Charger la matrice de similarité
            similarity_path = mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path="similarity_matrix"
            )
            self.cosine_sim = np.load(f"{similarity_path}/similarity_matrix.npy")
    
    def recommend(self, title, top_n=5):
        if title not in self.indices:
            return []
            
        idx = self.indices[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        
        movie_indices = [i[0] for i in sim_scores]
        
        # Récupérer les films depuis la base de données
        session = get_db_session(self.db_url)
        movies = get_movies_by_ids(session, movie_indices)
        session.close()
        
        return [{
            'id': m.id,
            'title': m.title,
            'year': m.year,
            'genres': m.genres,
            'rating': m.rating,
            'overview': m.overview
        } for m in movies]