import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import plotly.express as px

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Système de Recommandation de Films")

@st.cache_data
def load_movies():
    response = requests.get(f"{BACKEND_URL}/movies")
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data
def get_recommendations(movie_title, top_n=5):
    response = requests.post(
        f"{BACKEND_URL}/recommend",
        json={"movie_title": movie_title, "top_n": top_n}
    )
    if response.status_code == 200:
        return response.json()
    return []

movies = load_movies()
movie_titles = [movie['title'] for movie in movies]

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Paramètres")
    selected_movie = st.selectbox("Choisissez un film que vous aimez:", movie_titles)
    top_n = st.slider("Nombre de recommandations:", 1, 10, 5)
    
    if st.button("Obtenir des recommandations"):
        recommendations = get_recommendations(selected_movie, top_n)
        
        if recommendations:
            st.success("Voici les films recommandés:")
            for i, movie in enumerate(recommendations, 1):
                st.markdown(f"{i}. **{movie['title']}** ({movie['year']})")
                st.caption(f"Genres: {movie['genres']}")
                st.caption(f"Note: {movie['rating']}/10")
                st.write(movie['overview'])
                st.divider()

with col2:
    st.header("Tous les Films")
    df = pd.DataFrame(movies)
    
    # Filtres
    year_range = st.slider(
        "Filtrer par année:",
        min_value=int(df['year'].min()),
        max_value=int(df['year'].max()),
        value=(int(df['year'].min()), int(df['year'].max()))
    
    rating_filter = st.slider(
        "Filtrer par note minimale:",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.5)
    
    filtered_df = df[
        (df['year'] >= year_range[0]) & 
        (df['year'] <= year_range[1]) & 
        (df['rating'] >= rating_filter)
    ]
    
    # Visualisation
    fig = px.scatter(
        filtered_df,
        x='year',
        y='rating',
        hover_data=['title', 'genres'],
        color='genres',
        title="Distribution des films par année et note"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des films
    st.dataframe(filtered_df[['title', 'year', 'genres', 'rating']], height=400)