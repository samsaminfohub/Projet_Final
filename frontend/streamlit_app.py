import streamlit as st
import requests

st.title("ML Mental Health Predictor")

text = st.text_area("Enter your text")

if st.button("Predict"):
    if text.strip():
        response = requests.post("http://backend:8000/predict", json={"text": text})
        if response.status_code == 200:
            result = response.json()
            st.success(f"Prediction: {result['prediction']}")
        else:
            st.error("API error")
    else:
        st.warning("Please enter some text.")
