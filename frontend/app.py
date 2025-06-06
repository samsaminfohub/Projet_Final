import streamlit as st
import requests

API_URL = "http://20.62.91.133:8000"

st.title("Gestionnaire de tâches")
if st.button("Afficher les tâches"):
    response = requests.get(f"{API_URL}/tasks")
    if response.ok:
        for task in response.json():
            st.write(f"- {task['title']} : {task['description']} (✔️)" if task['completed'] else f"(❌)")