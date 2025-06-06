# frontend/app.py
import streamlit as st
import requests

st.title("MiniLab2 Dashboard")

# Connect to the backend API
BACKEND_URL = "http://backend:8000"

# Data fetching function
def fetch_data():
    try:
        response = requests.get(f"{BACKEND_URL}/data/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# Display data
data = fetch_data()
if data:
    st.subheader("Experiment Data")
    st.table(data)
else:
    st.warning("No data available")

# Data input form
with st.form("add_data_form"):
    st.subheader("Add New Data")
    exp_name = st.text_input("Experiment Name")
    param1 = st.number_input("Parameter 1")
    param2 = st.number_input("Parameter 2")
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        new_data = {
            "experiment_name": exp_name,
            "parameter1": float(param1),
            "parameter2": float(param2)
        }
        response = requests.post(f"{BACKEND_URL}/data/", json=new_data)
        if response.status_code == 200:
            st.success("Data added successfully!")
        else:
            st.error("Error adding data")
                        