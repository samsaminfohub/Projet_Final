import pandas as pd
from sqlalchemy import create_engine
from models import Base, Movie
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    # Connexion à la base de données
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    # Création des tables
    Base.metadata.create_all(engine)
    
    # Session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Vérifier si la base est déjà peuplée
    if session.query(Movie).count() == 0:
        # Charger les données depuis le CSV
        df = pd.read_csv("data/movies.csv")
        
        # Nettoyage des données
        df = df.dropna()
        df['year'] = df['title'].str.extract(r'\((\d{4})\)')
        df['title'] = df['title'].str.replace(r'\(\d{4}\)', '').str.strip()
        
        # Insertion des films
        for _, row in df.iterrows():
            movie = Movie(
                title=row['title'],
                genres=row['genres'],
                year=int(row['year']) if pd.notna(row['year']) else None,
                rating=float(row['rating']) if pd.notna(row['rating']) else None,
                overview=row['overview'],
                director=row['director'],
                actors=row['actors']
            )
            session.add(movie)
        
        session.commit()
        print("Base de données initialisée avec succès!")
    else:
        print("La base de données contient déjà des données.")
    
    session.close()

if __name__ == "__main__":
    init_db()