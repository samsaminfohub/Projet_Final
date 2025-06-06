import pandas as pd
import requests
from io import StringIO
import os

def download_movie_data():
    # URL d'un dataset exemple (à remplacer par votre propre source)
    url = "https://raw.githubusercontent.com/amirziai/sklearnflask/master/movies.csv"
    
    response = requests.get(url)
    if response.status_code == 200:
        # Légère transformation des données pour correspondre à notre schéma
        df = pd.read_csv(StringIO(response.text))
        
        # Ajout de colonnes manquantes
        if 'overview' not in df.columns:
            df['overview'] = "Description non disponible"
        if 'director' not in df.columns:
            df['director'] = "Inconnu"
        if 'actors' not in df.columns:
            df['actors'] = "Inconnu"
        
        # Sauvegarde
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/movies.csv", index=False)
        print("Données téléchargées avec succès!")
    else:
        print("Échec du téléchargement des données")

if __name__ == "__main__":
    download_movie_data()