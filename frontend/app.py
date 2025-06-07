import streamlit as st
import requests

st.title("Prédicteur de Risque de Santé Mentale")

feature1 = st.number_input("Caractéristique 1")
feature2 = st.number_input("Caractéristique 2")

if st.button("Prédire"):
    response = requests.post("http://backend:8000/predict/", json={
        "feature1": feature1,
        "feature2": feature2
    })
    if response.status_code == 200:
        prediction = response.json()["prediction"]
        st.success(f"Prédiction : {prediction}")
    else:
        st.error("Erreur lors de la prédiction.")
